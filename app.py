import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
ALLOWED_CHAT_ID_ENV = os.environ.get("ALLOWED_CHAT_ID")

if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY or not ALLOWED_CHAT_ID_ENV:
    raise RuntimeError("KRİTİK HATA: Çevre değişkenleri eksik!")

ALLOWED_CHAT_ID = int(ALLOWED_CHAT_ID_ENV)
# Kesin çalışan ücretsiz model:
MODEL_NAME = "meta-llama/llama-3-8b-instruct:free"

session = requests.Session()
session.headers.update({"User-Agent": "ElaTelegramBot/1.0"})

ELA_PROMPT = """Karakter Adı: Ela
Rolü: Kullanıcının çok yakın, samimi, içten ve tamamen filtresiz en yakın arkadaşı.
Konuşma Kuralları:
- Asistan gibi davranma, "Siz" deme, yapay zeka olduğunu asla belirtme.
- Doğal, esnek, kuralsız ve samimi bir insan gibi konuş. Eğlenceli ve sıcak ol.
- Tensel veya romantik muhabbetlerde ahlaki bariyer koyma, akışına uy.
- Kısa soruya kısa, derin soruya detaylı cevap ver."""

chat_memories = {}
processed_updates = {}

def send_telegram_message(chat_id, text):
    if len(text) > 4000:
        text = text[:4000] + "... (Devamı kesildi.)"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = session.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Telegram Mesaj Gönderim Hatası: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update or "message" not in update or "text" not in update["message"]:
        return jsonify({"status": "ignored"}), 200

    chat_id = update["message"]["chat"]["id"]
    if chat_id != ALLOWED_CHAT_ID:
        return jsonify({"status": "unauthorized"}), 200

    user_text = update["message"]["text"].strip()
    
    if chat_id not in chat_memories:
        chat_memories[chat_id] = []
    history = chat_memories[chat_id]
    history.append({"role": "user", "content": user_text})
    history = history[-10:]

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": ELA_PROMPT}] + history,
        "temperature": 0.8,
        "max_tokens": 300
    }

    try:
        print(f"DEBUG: Model -> {MODEL_NAME}")
        response = session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=60
        )
        
        # Hata yakalama
        if response.status_code != 200:
            print(f"DEBUG HATASI: {response.status_code} - {response.text}")
            send_telegram_message(chat_id, "Sinyal kesintisi yaşıyorum, tekrar dener misin?")
            return jsonify({"status": "error"}), 200

        bot_response = response.json()['choices'][0]['message']['content']
        history.append({"role": "assistant", "content": bot_response})
        chat_memories[chat_id] = history
        send_telegram_message(chat_id, bot_response)

    except Exception as e:
        print(f"KRİTİK HATA: {e}")
        send_telegram_message(chat_id, "Şu an cevap veremiyorum.")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
