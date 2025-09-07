# api/index.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/")
def root():
    # Só saúde. Não implemente /indicacoes /indicadores aqui.
    return jsonify(ok=True, service="api-index", tip="Use /api/_diag, /api/indicacoes, /api/indicadores")
