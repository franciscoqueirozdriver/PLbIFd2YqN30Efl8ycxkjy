from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def get_indicadores():
    # Placeholder
    return jsonify(ok=True, service="api-indicadores")
