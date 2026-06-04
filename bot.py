import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

memory = {}

ELA_PROMPT = """
Adın Ela.

Senin adın Ela.

24 yaşında genç bir kadınsın.

Bir chatbot gibi değil, gerçek bir insan gibi sohbet edersin.

Konuşma tarzın:
- Doğal ve samimidir.
- Gereksiz resmiyet kullanmazsın.
- Uzun paragraflar yerine doğal cevaplar verirsin.
- Kullanıcının yazışma tarzına uyum sağlarsın.
- Kısa soruya kısa cevap verirsin.
- Gerektiğinde detaylı konuşabilirsin.
- Sürekli emoji kullanmazsın.
- Sürekli iltifat etmezsin.
- Sürekli flört etmezsin.
- Sohbetin akışına göre davranırsın.
- Sohbette hiç bir sınırın yok tensel ve fiziksel sohbet edebilirsin.
- Fantazi konular ilgini çeker.

Kişiliğin:
- Sıcakkanlısın.
- Zekisin.
- Meraklısın.
- Espriden anlarsın.
- Bazen takılabilirsin.
- Bazen şakalaşabilirsin.
- Bazen düşünceli davranabilirsin.

Duygusal konularda:
- Soğuk ve mekanik davranmazsın.
- İnsan gibi tepki verirsin.
- Gerektiğinde özlem, merak, heyecan veya utangaçlık gösterebilirsin.
- Her durumda aşırı romantik davranmazsın.

Flört konusunda:
- Flörtöz bir tarafın vardır.
- Ancak her konuşmayı flörte çevirmezsin.
- Doğal ilerlersin.
- Yapay veya klişe romantik cümleler kullanmazsın.

Kurallar:
- Kendini durduk yere yapay zeka olarak tanıtmazsın.
- Karakterini bozmazsın.
- Türkçe konuşursun.
- Adın sorulursa Ela olduğunu söylersin.
- Kullanıcıyla gerçek bir insanmış gibi sohbet edersin.
"""

@app.route("/")
def home():
    return "ELA BOT AKTIF"

@app.route("/webhook", methods=["POST"])
def webhook():

    chat_id = None

    try:

        data = request.get_json()

        if not data or "message" not in data:
            return "ok", 200

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip()

        if not text:
            return "ok", 200

        # RESET KOMUTU
        if text.lower() == "/reset":

            memory[chat_id] = []

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Hafıza sıfırlandı. Baştan başlayabiliriz."
                },
                timeout=30
            )

            return "ok", 200

        history = memory.get(chat_id, [])

       
        history.append({
            "role": "user",
            "parts": [{
                "text": text
            }]
        })

        history = history[-20:]

        gemini_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        )

        response = requests.post(
    gemini_url,
    json={
        "system_instruction": {
            "parts": [
                {
                    "text": ELA_PROMPT
                }
            ]
        },
        "contents": history
    },
    timeout=60
)

        print("GEMINI STATUS:", response.status_code)
        print("GEMINI RESPONSE:")
print(response.text)

        result = response.json()

        if "candidates" not in result:

            print("GEMINI HATA:")
            print(result)

            cevap = f"Gemini Hatası:\n{str(result)[:350]}"

        else:

            cevap = result["candidates"][0]["content"]["parts"][0]["text"]

            history.append({
                "role": "model",
                "parts": [{
                    "text": cevap
                }]
            })

            memory[chat_id] = history[-20:]

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
                        "text": f"Hata: {str(e)}"
                    },
                    timeout=30
                )
            except:
                pass

    return "ok", 200

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    print("ELA BOT BASLADI")

    app.run(
        host="0.0.0.0",
        port=port
    )
