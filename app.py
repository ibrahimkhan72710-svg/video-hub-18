import os
from flask import Flask, request, jsonify, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__, static_folder="public", static_url_path="")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "VIPprivatevideo10_bot")
PORT = int(os.getenv("PORT", "5000"))

@app.get("/")
def home():
    return send_from_directory("public", "index.html")

@app.get("/health")
def health():
    return jsonify(status="ok", service="Video Hub 18+")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("ওয়েবসাইট খুলুন / Open website", url=os.getenv("SITE_URL", "https://example.com"))]]
    await update.message.reply_text(
        "স্বাগতম Video Hub 18+ এ। কেবল ১৮ বছর বা তার বেশি বয়সীদের জন্য। "
        "শুধু আইনসম্মত, সম্মতিপূর্ণ এবং আপনার নিজের/অনুমতিপ্রাপ্ত ভিডিও শেয়ার করুন।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def run_bot():
    if not BOT_TOKEN:
        print("BOT_TOKEN সেট করা নেই; শুধু ওয়েবসাইট চালু হবে।")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    # For simple hosting, set RUN_BOT=1 to start polling in this process.
    if os.getenv("RUN_BOT") == "1":
        import threading
        threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
