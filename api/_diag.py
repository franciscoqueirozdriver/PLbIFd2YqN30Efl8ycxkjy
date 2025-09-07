from flask import Flask, jsonify
import traceback
from ._sheets import ws

app = Flask(__name__)

@app.get("/")
def diag():
    try:
        headers = ws("Indicacoes").row_values(1)
        return jsonify(ok=True, headers=headers)
    except Exception as e:
        return jsonify(ok=False, error=str(e), trace=traceback.format_exc()), 500
