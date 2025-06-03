from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import openai
import os

app = Flask(__name__)
CORS(app)


OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")
    file = request.files.get("file")

    headers = {
        "Authorization": f"Bearer: {OPEN_AI_API_KEY}",
    }

    if file:
        files = {
            "file": (file.filename, file.stream, file.mimetype),
        }
        data = {
            "input": user_message or "",
            "model": "gpt-3.5-turbo",
        }
        response = requests.post(
            OPENAI_RESPONSES_URL,
            headers=headers,
            data=data,
            files=files,
        )
    else:
        json_data = {
            "input": user_message,
            "model": "gpt-3.5-turbo",
        }
        headers["Content-Type"] = "application/json"
        response = requests.post(
            OPENAI_RESPONSES_URL,
            headers=headers,
            json=json_data,
        )

    if response.ok:
        result = response.json()
        reply = result.get("output") or result.get("choices", [{}])[0].get(
            "text", "No reply found."
        )
        return jsonify({"reply": reply})
    else:
        return jsonify({"reply": f"Error: {response.text}"}), response.status_code


if __name__ == "__main__":
    app.run(port=8000, debug=True)
