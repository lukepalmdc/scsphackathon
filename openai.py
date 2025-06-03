
from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")
client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    try:
        # Stream response from OpenAI and collect the content
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            stream=True
        )
        reply = ""
        for chunk in stream:
            content = getattr(chunk.choices[0].delta, "content", None)
            if content:
                reply += content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)
