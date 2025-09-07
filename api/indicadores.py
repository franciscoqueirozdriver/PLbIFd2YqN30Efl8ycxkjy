import json
from flask import Flask, request

from ._utils import ok, json_error, iso_now, parse_int
from ._sheets import get_rows, get_by_id, insert_rows, update_row, soft_delete, append_log
from ._validators import validate_indicador_create, validate_indicador_update
from ._rbac import tem_permissao
from ._ids import next_id

app = Flask(__name__)


def _user_type() -> str:
    return request.headers.get("X-User-Type", "admin")


@app.route("/", methods=["OPTIONS"])
def options_root():
    return ok()


@app.get("/")
def list_indicadores():
    if not tem_permissao(_user_type(), "indicadores", "visualizar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    limit = parse_int(request.args.get("limit"), 50)
    cursor = parse_int(request.args.get("cursor"), None)
    filtros = {}
    telefone = request.args.get("telefone")
    if telefone:
        filtros["telefone"] = telefone
    res = get_rows("Indicadores", filters=filtros, limit=limit, cursor=cursor)
    rows = res["rows"]
    nome = request.args.get("nome")
    if nome:
        rows = [r for r in rows if nome.lower() in str(r.get("nome", "")).lower()]
    email = request.args.get("email")
    if email:
        rows = [r for r in rows if str(r.get("email", "")).lower() == email.lower()]
    return ok(data=rows, total=res["total"], cursor=res["next_cursor"])


@app.post("/")
def create_indicador():
    if not tem_permissao(_user_type(), "indicadores", "editar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    try:
        data = request.get_json(force=True)
        validate_indicador_create(data)
    except ValueError as e:
        return json_error(400, "VALIDATION_ERROR", str(e))
    total = get_rows("Indicadores", limit=1000000)["total"]
    indicador_id = next_id("IND", total + 1)
    now = iso_now()
    record = {
        "indicador_id": indicador_id,
        "nome": data["nome"],
        "telefone": data["telefone"],
        "email": data.get("email", ""),
        "empresa": data.get("empresa", ""),
        "created_at": now,
        "updated_at": now,
        "status": "active",
    }
    insert_rows("Indicadores", [record])
    try:
        log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
        append_log(log_id=log_id, tab="Indicadores", ref_id=indicador_id, acao="insert",
                   ator=_user_type(), payload=json.dumps(record), timestamp=now)
    except Exception:
        pass
    return ok(id=indicador_id), 201


@app.put("/<indicador_id>")
def update_indicador(indicador_id: str):
    if not tem_permissao(_user_type(), "indicadores", "editar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    existing = get_by_id("Indicadores", "indicador_id", indicador_id)
    if not existing or existing.get("status") == "archived":
        return json_error(404, "NOT_FOUND", "Indicador não encontrado")
    try:
        data = request.get_json(force=True)
        validate_indicador_update(indicador_id, data)
    except ValueError as e:
        return json_error(400, "VALIDATION_ERROR", str(e))
    data["updated_at"] = iso_now()
    update_row("Indicadores", "indicador_id", indicador_id, data)
    try:
        log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
        append_log(log_id=log_id, tab="Indicadores", ref_id=indicador_id, acao="update",
                   ator=_user_type(), payload=json.dumps(data), timestamp=data["updated_at"])
    except Exception:
        pass
    return ok(id=indicador_id)


@app.delete("/<indicador_id>")
def delete_indicador(indicador_id: str):
    if not tem_permissao(_user_type(), "indicadores", "excluir"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    existing = get_by_id("Indicadores", "indicador_id", indicador_id)
    if not existing or existing.get("status") == "archived":
        return json_error(404, "NOT_FOUND", "Indicador não encontrado")
    dep = get_rows("Indicacoes", filters={"indicador_id": indicador_id}, limit=1)["rows"]
    if dep:
        return json_error(409, "CONFLICT", "Indicador possui indicações")
    soft_delete("Indicadores", "indicador_id", indicador_id)
    try:
        log_id = next_id("LOG", get_rows("Logs", limit=1000000)["total"] + 1)
        append_log(log_id=log_id, tab="Indicadores", ref_id=indicador_id, acao="delete",
                   ator=_user_type(), payload=json.dumps({}), timestamp=iso_now())
    except Exception:
        pass
    return ok(id=indicador_id)
