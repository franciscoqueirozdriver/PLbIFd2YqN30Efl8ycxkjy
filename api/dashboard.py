from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def dashboard():
    return jsonify(ok=True, service="dashboard")
