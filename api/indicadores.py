from flask import Flask, jsonify
from ._sheets import ws
from ._utils import ok, err
import traceback

app = Flask(__name__)

@app.get("/")
def get_indicadores():
    try:
        records = ws("Indicadores").get_all_records()
        return ok(records)
    except Exception as e:
        return err(500, "INDICADORES_ERROR", "Erro ao buscar indicadores", {
            "error": str(e),
            "trace": traceback.format_exc()
        })
