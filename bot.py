import os
import threading
import asyncio

from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

print("SURUM TEST 2026")

web_app = Flask(__name__)

@web_app.route("/")
def home():
    print("WEB ISTEGI GELDI")
    return "Bot Aktif"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    print("FLASK BASLIYOR PORT:", port)
    web_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/START CALISTI")
    await update.message.reply_text("Bot çalışıyor ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("MESAJ:", update.message.text)
    await update.message.reply_text(
        f"Yazdığın mesaj: {update.message.text}"
    )

def main():

    print("MAIN BASLADI")

    token = os.getenv("BOT_TOKEN")

    print("TOKEN VAR:", bool(token))

    application = Application.builder().token(token).build()

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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application.run_polling(
        drop_pending_updates=True
    )

if __name__ == "__main__":
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    main()
