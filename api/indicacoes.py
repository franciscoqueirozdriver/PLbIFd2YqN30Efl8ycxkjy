import json
from flask import Flask, request

from ._utils import ok, json_error, iso_now, parse_int
from ._sheets import (
    get_rows,
    get_by_id,
    insert_rows,
    update_row,
    soft_delete,
    append_log,
)
from ._validators import (
    validate_indicador_create,
    validate_indicacao_create,
    validate_indicacao_update,
)
from ._rbac import tem_permissao
from ._ids import next_id

app = Flask(__name__)


def _user_type() -> str:
    return request.headers.get("X-User-Type", "admin")


@app.route("/", methods=["OPTIONS"])
def options_root():
    return ok()


@app.get("/")
def list_indicacoes():
    if not tem_permissao(_user_type(), "indicacoes", "visualizar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    limit = parse_int(request.args.get("limit"), 50)
    cursor = parse_int(request.args.get("cursor"), None)
    filtros = {}
    for f in ["indicador_id", "gerou_venda", "status_recompensa"]:
        val = request.args.get(f)
        if val is not None:
            filtros[f] = val
    res = get_rows("Indicacoes", filters=filtros, limit=limit, cursor=cursor)
    rows = res["rows"]
    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")
    if data_ini:
        rows = [r for r in rows if r.get("data_indicacao") >= data_ini]
    if data_fim:
        rows = [r for r in rows if r.get("data_indicacao") <= data_fim]
    return ok(data=rows, total=res["total"], cursor=res["next_cursor"])


@app.post("/")
def create_indicacao():
    if not tem_permissao(_user_type(), "indicacoes", "editar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    try:
        data = request.get_json(force=True)
    except Exception:
        return json_error(400, "BAD_REQUEST", "JSON inválido")
    indicador_payload = data.get("indicador")
    if indicador_payload:
        try:
            validate_indicador_create(indicador_payload)
        except ValueError as e:
            return json_error(400, "VALIDATION_ERROR", str(e))
        existing = get_rows("Indicadores", filters={"telefone": indicador_payload["telefone"]}, limit=1)["rows"]
        if existing:
            indicador_id = existing[0]["indicador_id"]
        else:
            total_i = get_rows("Indicadores", limit=1000000)["total"]
            indicador_id = next_id("IND", total_i + 1)
            now = iso_now()
            record_i = {
                "indicador_id": indicador_id,
                "nome": indicador_payload["nome"],
                "telefone": indicador_payload["telefone"],
                "email": indicador_payload.get("email", ""),
                "empresa": indicador_payload.get("empresa", ""),
                "created_at": now,
                "updated_at": now,
                "status": "active",
            }
            insert_rows("Indicadores", [record_i])
            try:
                log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
                append_log(log_id=log_id, tab="Indicadores", ref_id=indicador_id, acao="insert",
                           ator=_user_type(), payload=json.dumps(record_i), timestamp=now)
            except Exception:
                pass
        data["indicador_id"] = indicador_id
    if "indicador_id" not in data:
        return json_error(400, "VALIDATION_ERROR", "indicador_id é obrigatório")
    try:
        validate_indicacao_create(data)
    except ValueError as e:
        return json_error(400, "VALIDATION_ERROR", str(e))
    total = get_rows("Indicacoes", limit=1000000)["total"]
    indicacao_id = next_id("INC", total + 1)
    now = iso_now()
    record = {
        "indicacao_id": indicacao_id,
        "indicador_id": data["indicador_id"],
        "data_indicacao": data["data_indicacao"],
        "nome_indicado": data["nome_indicado"],
        "telefone_indicado": data["telefone_indicado"],
        "gerou_venda": data.get("gerou_venda", False),
        "faturamento_gerado": data.get("faturamento_gerado", 0),
        "status_recompensa": data.get("status_recompensa", "Nao"),
        "observacoes": data.get("observacoes", ""),
        "created_at": now,
        "updated_at": now,
        "status": "active",
    }
    insert_rows("Indicacoes", [record])
    try:
        log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
        append_log(log_id=log_id, tab="Indicacoes", ref_id=indicacao_id, acao="insert",
                   ator=_user_type(), payload=json.dumps(record), timestamp=now)
    except Exception:
        pass
    return ok(id=indicacao_id), 201


@app.put("/<indicacao_id>")
def update_indicacao(indicacao_id: str):
    if not tem_permissao(_user_type(), "indicacoes", "editar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    existing = get_by_id("Indicacoes", "indicacao_id", indicacao_id)
    if not existing or existing.get("status") == "archived":
        return json_error(404, "NOT_FOUND", "Indicação não encontrada")
    try:
        data = request.get_json(force=True)
        validate_indicacao_update(existing, data)
    except ValueError as e:
        return json_error(400, "VALIDATION_ERROR", str(e))
    data["updated_at"] = iso_now()
    update_row("Indicacoes", "indicacao_id", indicacao_id, data)
    try:
        log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
        append_log(log_id=log_id, tab="Indicacoes", ref_id=indicacao_id, acao="update",
                   ator=_user_type(), payload=json.dumps(data), timestamp=data["updated_at"])
    except Exception:
        pass
    return ok(id=indicacao_id)


@app.delete("/<indicacao_id>")
def delete_indicacao(indicacao_id: str):
    if not tem_permissao(_user_type(), "indicacoes", "excluir"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    existing = get_by_id("Indicacoes", "indicacao_id", indicacao_id)
    if not existing or existing.get("status") == "archived":
        return json_error(404, "NOT_FOUND", "Indicação não encontrada")
    soft_delete("Indicacoes", "indicacao_id", indicacao_id)
    try:
        log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
        append_log(log_id=log_id, tab="Indicacoes", ref_id=indicacao_id, acao="delete",
                   ator=_user_type(), payload=json.dumps({}), timestamp=iso_now())
    except Exception:
        pass
    return ok(id=indicacao_id)
