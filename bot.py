import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

active_character = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"Merhaba. /ela veya /emre yazarak karakter seçebilirsin."
)

async def ela(update: Update, context: ContextTypes.DEFAULT_TYPE):
active_character[update.effective_chat.id] = "Ela"
await update.message.reply_text("Ela seninle konuşmaya hazır. 💙")

async def emre(update: Update, context: ContextTypes.DEFAULT_TYPE):
active_character[update.effective_chat.id] = "Emre"
await update.message.reply_text("Emre burada. 😎")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
chat_id = update.effective_chat.id
character = active_character.get(chat_id, "Ela")

```
if character == "Ela":
    await update.message.reply_text(
        f"Ela: Seni duydum. Şimdilik test modundayım. Yazdığın: {update.message.text}"
    )
else:
    await update.message.reply_text(
        f"Emre: Mesajını aldım. Şimdilik test modundayım. Yazdığın: {update.message.text}"
    )
```

def main():
token = os.getenv("BOT_TOKEN")

```
if not token:
    raise ValueError("BOT_TOKEN bulunamadı")

app = Application.builder().token(token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ela", ela))
app.add_handler(CommandHandler("emre", emre))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
```

if **name** == "**main**":
main()
