import base64
import os

import requests
from flask import Flask, jsonify, render_template, request

MODEL_URL = os.getenv("MODEL_URL", "http://localhost:5050")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/classify", methods=["POST"])
def classify():
    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify({"error": "No image uploaded."}), 400

    data = base64.b64encode(file.read()).decode()
    data_uri = f"data:{file.mimetype};base64,{data}"

    try:
        resp = requests.post(
            f"{MODEL_URL}/predictions",
            json={"input": {"image": data_uri}},
            timeout=120,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Model request failed: {e}"}), 502

    result = resp.json()
    if result.get("status") != "succeeded":
        return jsonify({"error": result.get("error", "Prediction failed.")}), 502

    return jsonify({"predictions": result["output"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)