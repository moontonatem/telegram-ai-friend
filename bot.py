import os
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Telegram AI Friend Online"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

active_character = {}

ELA_PROMPT = """
Sen Ela'sın.
35 yaşındasın.
Türkçe konuşursun.
"""

EMRE_PROMPT = """
Sen Emre'sin.
35 yaşındasın.
Türkçe konuşursun.
"""

def ask_ai(character_prompt, message):

    print("AI ISTEGI GONDERILIYOR")

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
                {"role": "system", "content": character_prompt},
                {"role": "user", "content": message}
            ]
        },
        timeout=60
    )

    print("STATUS:", response.status_code)

    data = response.json()

    return data["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start CALISTI")
    await update.message.reply_text("Bot aktif")

async def ela(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/ela CALISTI")
    active_character[update.effective_chat.id] = "Ela"
    await update.message.reply_text("Ela aktif")

async def emre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/emre CALISTI")
    active_character[update.effective_chat.id] = "Emre"
    await update.message.reply_text("Emre aktif")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("MESAJ:", update.message.text)

    chat_id = update.effective_chat.id
    character = active_character.get(chat_id, "Ela")

    try:
        if character == "Ela":
            answer = ask_ai(ELA_PROMPT, update.message.text)
        else:
            answer = ask_ai(EMRE_PROMPT, update.message.text)

        await update.message.reply_text(answer)

    except Exception as e:
        print("HATA:", str(e))
        await update.message.reply_text(f"Hata: {str(e)}")

def main():

    token = os.getenv("BOT_TOKEN")

    print("BOT BASLADI")
    print("TOKEN VAR:", bool(token))

    app = Application.builder().token(token).build()

    print("HANDLER EKLENIYOR")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ela", ela))
    app.add_handler(CommandHandler("emre", emre))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("POLLING BASLIYOR")

    app.run_polling(
    drop_pending_updates=True,
    close_loop=False
)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()
