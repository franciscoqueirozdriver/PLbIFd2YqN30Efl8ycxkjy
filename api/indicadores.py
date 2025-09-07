from flask import Flask, jsonify
from ._sheets import ws
from ._utils import ok, err
import traceback

app = Flask(__name__)

@app.get("/")
def get_indicadores():
    try:
        records = ws("Indicadores").get_all_records()
        return jsonify(records)
    except Exception as e:
        return jsonify(ok=False, error="INDICADORES_ERROR", message=str(e), trace=traceback.format_exc()), 500
