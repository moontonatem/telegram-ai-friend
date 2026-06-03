import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot Calisiyor"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

active_character = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba. /ela veya /emre yazarak karakter sec.")

async def ela(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_character[update.effective_chat.id] = "Ela"
    await update.message.reply_text("Ela seninle konusmaya hazir.")

async def emre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_character[update.effective_chat.id] = "Emre"
    await update.message.reply_text("Emre burada.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    character = active_character.get(chat_id, "Ela")

    if character == "Ela":
        await update.message.reply_text("Ela: " + update.message.text)
    else:
        await update.message.reply_text("Emre: " + update.message.text)

def main():
    token = os.getenv("BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ela", ela))
    app.add_handler(CommandHandler("emre", emre))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()
