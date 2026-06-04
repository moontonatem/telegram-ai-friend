import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route("/")
def home():
    return "BOT ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.get_json()

        print("=" * 50)
        print(data)
        print("=" * 50)

        if "message" not in data:
            return "ok", 200

        chat_id = data["message"]["chat"]["id"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "Webhook çalışıyor 🚀"
            },
            timeout=30
        )

    except Exception as e:

        print("HATA:")
        print(repr(e))

    return "ok", 200

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    print("WEBHOOK CEVAP TESTI")

    app.run(
        host="0.0.0.0",
        port=port
    )
