import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("BOT DOSYASI YUKLENDI")

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot Aktif"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start CALISTI")
    await update.message.reply_text("Bot aktif çalışıyor ✅")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/test CALISTI")
    await update.message.reply_text("Test başarılı 🚀")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("MESAJ:", update.message.text)
    await update.message.reply_text(
        f"Yazdığın mesaj: {update.message.text}"
    )

def main():

    token = os.getenv("BOT_TOKEN")

    print("BOT BASLADI")
    print("TOKEN VAR:", bool(token))

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    )

    print("POLLING BASLIYOR")

    application.run_polling(
        drop_pending_updates=True
    )

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    main()
