from flask import Flask, jsonify

app = Flask(__name__)


def next_id(prefix: str, seq: int) -> str:
    return f"{prefix}_{seq:04d}"


@app.get("/")
def root():
    return jsonify(ok=True, service="ids", tip="Use next_id(prefix, seq)")

