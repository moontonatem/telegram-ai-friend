import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
ALLOWED_CHAT_ID = int(os.environ.get("ALLOWED_CHAT_ID"))

MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"
ELA_PROMPT = "Sen Ela'sın. Kullanıcının yakın arkadaşısın, samimi ve filtresiz konuşursun."

chat_memories = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update or "message" not in update: return jsonify({"ok": True}), 200
    
    chat_id = update["message"]["chat"]["id"]
    user_text = update["message"]["text"].strip()

    if chat_id not in chat_memories: chat_memories[chat_id] = []
    history = chat_memories[chat_id][-10:]
    history.append({"role": "user", "content": user_text})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "system", "content": ELA_PROMPT}] + history,
                "temperature": 0.7,
                "max_tokens": 200
            },
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=30
        )
        
        # HATAYI YAKALA VE TELEGRAM'A GÖNDER
        if response.status_code != 200:
            error_msg = f"Hata Kodu: {response.status_code}\nDetay: {response.text}"
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": error_msg})
            return jsonify({"status": "error"}), 200

        bot_response = response.json()['choices'][0]['message']['content']
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": bot_response})
        
        history.append({"role": "assistant", "content": bot_response})
        chat_memories[chat_id] = history
        
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": f"Kod Hatası: {str(e)}"})

    return jsonify({"ok": True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
