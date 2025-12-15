from __future__ import annotations

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health() -> tuple[dict, int]:
    return jsonify({"status": "ok", "service": "shop-app"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

