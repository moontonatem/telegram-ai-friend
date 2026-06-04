import os
import threading
import requests

from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

print("SURUM TEMIZ 2026")

# --------------------
# FLASK
# --------------------

web = Flask(__name__)

@web.route("/")
def home():
    return "BOT ONLINE"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    print("FLASK PORT:", port)
    web.run(host="0.0.0.0", port=port)

# --------------------
# OPENROUTER
# --------------------

def ask_ai(message):

    api_key = os.getenv("OPENROUTER_API_KEY")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
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
                    "content": message
                }
            ]
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]

# --------------------
# TELEGRAM
# --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        text = update.message.text

        print("MESAJ:", text)

        answer = ask_ai(text)

        await update.message.reply_text(answer)

    except Exception as e:

        print("HATA:", repr(e))

        await update.message.reply_text(
            f"Hata oluştu:\n{str(e)}"
        )

# --------------------
# MAIN
# --------------------

def main():

    print("MAIN BASLADI")

    token = os.getenv("BOT_TOKEN")

    if not token:
        print("BOT_TOKEN BULUNAMADI")
        return

    print("TOKEN OK")

    app = Application.builder().token(token).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("POLLING BASLADI")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

# --------------------
# START
# --------------------

if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    main()
