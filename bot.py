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

print("SURUM TEST 2026")

# --------------------
# FLASK
# --------------------

app_web = Flask(__name__)

@app_web.route("/")
def home():
    print("WEB ISTEGI GELDI")
    return "BOT AKTIF"

def run_web():
    port = int(os.getenv("PORT", 10000))
    print("FLASK BASLIYOR PORT:", port)
    app_web.run(host="0.0.0.0", port=port)

# --------------------
# AI
# --------------------

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_ai(message):

    api_key = os.getenv("OPENROUTER_API_KEY")

    response = requests.post(
        OPENROUTER_URL,
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

    print("AI STATUS:", response.status_code)

    data = response.json()

    return data["choices"][0]["message"]["content"]

# --------------------
# TELEGRAM
# --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start CALISTI")
    await update.message.reply_text("Bot aktif.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    print("MESAJ:", text)

    try:

        cevap = ask_ai(text)

        await update.message.reply_text(cevap)

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
        print("BOT_TOKEN YOK")
        return

    print("TOKEN VAR")

    application = (
        Application
        .builder()
        .token(token)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            echo
        )
    )

    print("POLLING BASLIYOR")

    application.run_polling(
        drop_pending_updates=True
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
