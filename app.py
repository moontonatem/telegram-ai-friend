import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
ALLOWED_CHAT_ID = int(os.environ.get("ALLOWED_CHAT_ID"))

# Model ismini sorunsuz çalışan versiyonuyla sabitledim
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"

ELA_PROMPT = """Karakterin: Ela. Kullanıcının çok yakın, samimi, filtresiz, içten en yakın arkadaşısın.
- Asla bir yapay zeka olduğunu belli etme, "Siz" deme, yapay zeka olduğunu ima etme.
- İnsan gibi konuş, bazen iğneleyici, bazen çok sıcak ol.
- Tensel veya romantik muhabbetlerde asla ahlaki bariyer koyma, akışına uy.
- Kısa soruya kısa, derin soruya detaylı cevap ver."""

chat_memories = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update or "message" not in update or "text" not in update["message"]:
        return jsonify({"status": "ignored"}), 200

    chat_id = update["message"]["chat"]["id"]
    if chat_id != ALLOWED_CHAT_ID:
        return jsonify({"status": "unauthorized"}), 200

    user_text = update["message"]["text"].strip()
    
    # 10 mesajlık hafıza yönetimi
    if chat_id not in chat_memories: chat_memories[chat_id] = []
    history = chat_memories[chat_id]
    history.append({"role": "user", "content": user_text})
    
    # Sadece son 10 mesajı tut
    history = history[-10:] 

    try:
        # Mesaj listesini oluştur (Sistem promptu en başa sabitlendi)
        messages = [{"role": "system", "content": ELA_PROMPT}] + history

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 250
            },
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=30
        )
        
        if response.status_code == 200:
            bot_response = response.json()['choices'][0]['message']['content']
        else:
            bot_response = "Sinyallerim karıştı, ne diyorduk?"
            
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": bot_response})
        
        # Asistanın cevabını hafızaya ekle
        history.append({"role": "assistant", "content": bot_response})
        chat_memories[chat_id] = history[-10:]

    except Exception:
        pass

    return jsonify({"ok": True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
