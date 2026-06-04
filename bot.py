import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route("/")
def home():
    return "BOT ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():

    chat_id = None

    try:

        data = request.get_json()

        if "message" not in data:
            return "ok", 200

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if not text:
            return "ok", 200

        gemini_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        )

        response = requests.post(
            gemini_url,
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": text
                            }
                        ]
                    }
                ]
            },
            timeout=60
        )

        print("GEMINI STATUS:", response.status_code)
        print(response.text)

        result = response.json()

        cevap = result["candidates"][0]["content"]["parts"][0]["text"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": cevap[:4000]
            },
            timeout=30
        )

    except Exception as e:

        print("HATA:", repr(e))

        if chat_id:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": f"Hata:\n{str(e)}"
                    },
                    timeout=30
                )
            except:
                pass

    return "ok", 200

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    print("GEMINI BOT BASLADI")

    app.run(
        host="0.0.0.0",
        port=port
    )
