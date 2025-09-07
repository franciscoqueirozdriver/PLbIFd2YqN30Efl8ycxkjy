from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def get_dashboard():
    # Placeholder
    return jsonify(ok=True, service="api-dashboard")
