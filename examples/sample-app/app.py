from flask import Flask, jsonify, request
import os
import subprocess

app = Flask(__name__)

API_TOKEN = os.environ.get("API_TOKEN", "changeme")


@app.route("/")
def hello():
    return jsonify(message="Hello, world!")


@app.route("/ping")
def ping():
    # Deliberately unsafe (see KNOWN_ISSUES.md #8): user input in a shell command.
    host = request.args.get("host", "localhost")
    out = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return jsonify(output=out.stdout)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
