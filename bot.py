import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/")
def home():
    return "BOT ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.get_json()

        if "message" not in data:
            return "ok", 200

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if not text:
            return "ok", 200

        ai = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Türkçe konuşan yardımcı bir asistansın."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            },
            timeout=60
        )

        cevap = ai.json()["choices"][0]["message"]["content"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": cevap
            },
            timeout=30
        )

    except Exception as e:

        print("HATA:", repr(e))

        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"Hata: {str(e)}"
                }
            )
        except:
            pass

    return "ok", 200

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    print("AI BOT BASLADI")

    app.run(
        host="0.0.0.0",
        port=port
    )
