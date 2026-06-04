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

    chat_id = None

    try:

        data = request.get_json()

        if not data:
            return "ok", 200

        if "message" not in data:
            return "ok", 200

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        print("=" * 50)
        print("GELEN MESAJ:", text)
        print("=" * 50)

        if not text:
            return "ok", 200

        ai = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "z-ai/glm-4.5-air",
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

        print("OPENROUTER STATUS:", ai.status_code)
        print("OPENROUTER CEVAP:")
        print(ai.text)

        data_ai = ai.json()

        if "choices" not in data_ai:

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"OpenRouter Hatası:\n{ai.text[:300]}"
                },
                timeout=30
            )

            return "ok", 200

        cevap = data_ai["choices"][0]["message"]["content"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": cevap
            },
            timeout=30
        )

    except Exception as e:

        print("GENEL HATA:")
        print(repr(e))

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

    print("AI BOT BASLADI")
    print("PORT:", port)

    app.run(
        host="0.0.0.0",
        port=port
    )
