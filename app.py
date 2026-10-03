import os, sqlite3, threading, logging
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

APP_NAME = "Video Hub 18+"
DB_PATH = os.getenv("DATABASE_PATH", "video_hub.db")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_BEFORE_DEPLOYING")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "").rstrip("/")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADS_DEMO_MODE = os.getenv("ADS_DEMO_MODE", "true").lower() == "true"
logging.basicConfig(level=logging.INFO)
bot_app = None

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            telegram_file_id TEXT DEFAULT '',
            video_url TEXT DEFAULT '',
            category TEXT DEFAULT 'অন্যান্য',
            active INTEGER DEFAULT 1
        )""")

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    with db() as con:
        videos = con.execute("SELECT id,title,description,category FROM videos WHERE active=1 ORDER BY id DESC").fetchall()
    return render_template("index.html", videos=videos, demo=ADS_DEMO_MODE)

@app.route("/age-confirm", methods=["POST"])
def age_confirm():
    session["age_confirmed"] = True
    return jsonify(ok=True)

@app.route("/ad-complete", methods=["POST"])
def ad_complete():
    # DEMO MODE ONLY: this is a visual test gate, NOT proof of a real ad impression.
    if not session.get("age_confirmed"):
        return jsonify(ok=False, error="আগে ১৮+ বয়স নিশ্চিত করুন।"), 403
    if not ADS_DEMO_MODE:
        # Replace this block with the ad network's signed server-to-server callback.
        return jsonify(ok=False, error="বিজ্ঞাপন নেটওয়ার্কের verified callback এখনো সংযুক্ত হয়নি।"), 501
    session["ads_done"] = min(6, int(session.get("ads_done", 0)) + 1)
    return jsonify(ok=True, count=session["ads_done"], unlocked=session["ads_done"] >= 6)

@app.route("/watch/<int:video_id>")
def watch(video_id):
    if not session.get("age_confirmed"):
        return redirect(url_for("home"))
    if int(session.get("ads_done", 0)) < 6:
        flash("ভিডিও দেখতে আগে ৬টি বিজ্ঞাপনের ধাপ সম্পন্ন করুন।")
        return redirect(url_for("home"))
    with db() as con:
        video = con.execute("SELECT * FROM videos WHERE id=? AND active=1", (video_id,)).fetchone()
    if not video:
        return "ভিডিও পাওয়া যায়নি", 404
    return render_template("watch.html", video=video)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if ADMIN_PASSWORD and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("পাসওয়ার্ড সঠিক নয়।")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin():
    with db() as con:
        videos = con.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    return render_template("admin.html", videos=videos)

@app.route("/admin/add", methods=["POST"])
@admin_required
def admin_add():
    title = request.form.get("title", "").strip()
    if not title:
        flash("ভিডিওর নাম লিখুন।")
        return redirect(url_for("admin"))
    with db() as con:
        con.execute("""INSERT INTO videos(title,description,telegram_file_id,video_url,category)
                       VALUES(?,?,?,?,?)""",
                    (title, request.form.get("description","").strip(),
                     request.form.get("telegram_file_id","").strip(),
                     request.form.get("video_url","").strip(),
                     request.form.get("category","অন্যান্য").strip()))
    flash("ভিডিও যোগ হয়েছে।")
    return redirect(url_for("admin"))

@app.route("/admin/toggle/<int:video_id>", methods=["POST"])
@admin_required
def admin_toggle(video_id):
    with db() as con:
        con.execute("UPDATE videos SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (video_id,))
    return redirect(url_for("admin"))

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "স্বাগতম Video Hub 18+ এ। এটি কেবল আইনসম্মত, সম্মতিপূর্ণ প্রাপ্তবয়স্কদের কনটেন্টের জন্য।"
    if WEBAPP_URL:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ওয়েবসাইট খুলুন", web_app=WebAppInfo(url=WEBAPP_URL))]])
        await update.message.reply_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text + "\nওয়েবসাইট URL সেট করা হয়নি।")

async def videos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with db() as con:
        rows = con.execute("SELECT id,title,telegram_file_id FROM videos WHERE active=1 ORDER BY id DESC").fetchall()
    if not rows:
        await update.message.reply_text("এখনো কোনো ভিডিও যোগ করা হয়নি।")
        return
    await update.message.reply_text("ভিডিও তালিকা:\n" + "\n".join(f"{r['id']}. {r['title']}" for r in rows) +
                                    "\n\nভিডিও পেতে /watch ID লিখুন।")
async def watch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("ব্যবহার: /watch 1")
        return
    vid = int(context.args[0])
    with db() as con:
        row = con.execute("SELECT * FROM videos WHERE id=? AND active=1", (vid,)).fetchone()
    if not row:
        await update.message.reply_text("ভিডিও পাওয়া যায়নি।")
    elif row["telegram_file_id"]:
        await update.message.reply_video(row["telegram_file_id"], caption=row["title"])
    elif row["video_url"]:
        await update.message.reply_text(f"{row['title']}\n{row['video_url']}")
    else:
        await update.message.reply_text("এই ভিডিওর Telegram file_id বা ভিডিও URL এখনো যোগ করা হয়নি।")

def run_bot():
    global bot_app
    if not BOT_TOKEN:
        logging.warning("BOT_TOKEN not set; Telegram bot is disabled.")
        return
    import asyncio
    async def runner():
        global bot_app
        bot_app = Application.builder().token(BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start_cmd))
        bot_app.add_handler(CommandHandler("videos", videos_cmd))
        bot_app.add_handler(CommandHandler("watch", watch_cmd))
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
        while True:
            await asyncio.sleep(3600)
    asyncio.run(runner())

init_db()
if __name__ == "__main__":
    if BOT_TOKEN:
        threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
