from flask import Flask, request, jsonify
import json, traceback
from ._sheets import append_rows, ensure_headers, SheetSchemaError, ws, list_rows
from ._utils import iso_now, ok, err, next_id

app = Flask(__name__)

HEADERS = [
    "indicacao_id","indicador_id","data_indicacao","nome_indicado","telefone_indicado",
    "gerou_venda","faturamento_gerado","status_recompensa","observacoes",
    "created_at","updated_at","created_by","updated_by","status"
]


def _total_rows():
    w = ws("Indicacoes")
    return max(0, len(w.get_all_values()) - 1)


@app.get("/")
def list_indicacoes():
    try:
        limit = max(1, min(200, int(request.args.get("limit", 50))))
        cursor = max(0, int(request.args.get("cursor", 0)))
        rows = list_rows("Indicacoes", HEADERS)
        total = len(rows)
        # ordena por created_at desc se existir; caso contrário, mantém ordem natural
        try:
            rows.sort(key=lambda r: r.get("created_at",""), reverse=True)
        except Exception:
            pass
        page = rows[cursor:cursor+limit]
        next_cursor = cursor + limit if cursor + limit < total else None
        return jsonify(ok=True, data=page, total=total, cursor=next_cursor)
    except SheetSchemaError as e:
        return err(500, "SHEET_SCHEMA_ERROR", str(e))
    except Exception as e:
        return jsonify(ok=False, error={"code":"UNEXPECTED","message":str(e),"trace":traceback.format_exc()}), 500


@app.post("/")
def create_indicacao():
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return err(400, "INVALID_JSON", "Corpo não é JSON válido")

    try:
        req = ["indicador_id","data_indicacao","nome_indicado","telefone_indicado"]
        miss = [k for k in req if not str(payload.get(k) or "").strip()]
        if miss:
            return err(422, "VALIDATION_ERROR", "Campos obrigatórios ausentes", {"missing": miss})

        gv = bool(payload.get("gerou_venda", False))
        fat = float(payload.get("faturamento_gerado", 0) or 0)
        if gv and fat <= 0:
            return err(422, "VALIDATION_ERROR", "faturamento_gerado deve ser > 0 quando gerou_venda=true")

        sr = (payload.get("status_recompensa") or "Nao")
        if sr not in ("Nao","EmProcessamento","Sim"):
            return err(422, "VALIDATION_ERROR", "status_recompensa inválido", {"permitidos":["Nao","EmProcessamento","Sim"]})

        total = _total_rows()
        inc_id = next_id("INC", total + 1)
        now = iso_now()
        row = {
            "indicacao_id": inc_id, "indicador_id": payload["indicador_id"],
            "data_indicacao": payload["data_indicacao"], "nome_indicado": payload["nome_indicado"],
            "telefone_indicado": payload["telefone_indicado"], "gerou_venda": gv,
            "faturamento_gerado": fat, "status_recompensa": sr, "observacoes": payload.get("observacoes",""),
            "created_at": now, "updated_at": now,
            "created_by": request.headers.get("X-User-Type","system"),
            "updated_by": request.headers.get("X-User-Type","system"),
            "status": "active",
        }
        append_rows("Indicacoes", [row], HEADERS)

        # Log best-effort
        try:
            from ._sheets import append_rows as _append
            _append("Logs", [{
                "log_id": f"LOG_{inc_id.split('_')[1]}","tab": "Indicacoes","ref_id": inc_id,
                "acao": "insert","ator": request.headers.get("X-User-Type","system"),
                "payload": json.dumps(payload, ensure_ascii=False),"timestamp": now
            }], ["log_id","tab","ref_id","acao","ator","payload","timestamp"])
        except Exception:
            pass

        return ok({"id": inc_id}, status=201)

    except SheetSchemaError as e:
        return err(500, "SHEET_SCHEMA_ERROR", str(e))
    except Exception as e:
        return jsonify(ok=False, error={"code":"UNEXPECTED","message":str(e),"trace":traceback.format_exc()}), 500

