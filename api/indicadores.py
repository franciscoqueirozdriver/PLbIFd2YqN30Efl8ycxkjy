from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def list_indicadores():
    return jsonify(ok=True, service="indicadores")
