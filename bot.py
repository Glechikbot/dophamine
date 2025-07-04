import os
import json
import random
import pytz
import threading
from datetime import time
from flask import Flask
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    JobQueue,
)

# === Налаштування через ENV ===
TOKEN       = os.environ["BOT_TOKEN"]
CHAT_ID     = os.environ["CHAT_ID"]
PORT        = int(os.environ.get("PORT", 8000))
TZ          = pytz.timezone("Europe/Kyiv")
ACTIVE_COUNT = 5  # скільки цитат тримати в quotes.json

# === Допоміжні функції ===
def load_quotes(path="quotes.json"):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# === Job-функції ===
async def send_random_quote(ctx: ContextTypes.DEFAULT_TYPE):
    quotes = load_quotes()
    await ctx.bot.send_message(chat_id=CHAT_ID, text=f"💀 {random.choice(quotes)}")
    delay = random.randint(3600, 3*3600)
    ctx.job_queue.run_once(send_random_quote, delay)

async def rotate_quotes(ctx: ContextTypes.DEFAULT_TYPE):
    with open('master_quotes.json', 'r', encoding='utf-8') as f:
        master = json.load(f)
    new = random.sample(master, k=min(ACTIVE_COUNT, len(master)))
    with open('quotes.json', 'w', encoding='utf-8') as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
    print(f"[Quotes rotated] {len(new)} items")

async def remind_todo(ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=CHAT_ID, text="⏰ Пора перевірити свій список справ!")

async def remind_no_reels(ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=CHAT_ID, text="🚫 Не залипай у рілсах, вперед до справ!")

async def remind_both(ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=CHAT_ID, text="🔃 Перевір справи та не забувай про рілси!")

async def remind_bedtime(ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=CHAT_ID, text="🌙 Час готуватися до сну. Вимикай екран, роби розтяжку.")

async def ping(update: ContextTypes.DEFAULT_TYPE, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот працює!")

def main():
    # 1) Запускаємо Flask-сервер для health-check у фоні
    flask_app = Flask(__name__)
    @flask_app.route("/")
    def health():
        return "OK", 200

    threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=PORT),
        daemon=True
    ).start()

    # 2) Налаштовуємо Telegram-додаток і JobQueue
    app = ApplicationBuilder().token(TOKEN).build()
    jq: JobQueue = app.job_queue

    # додамо /ping для тесту
    app.add_handler(CommandHandler("ping", ping))

    # ротація цитат: одразу й потім кожні 3 дні
    jq.run_once(rotate_quotes, when=0)
    jq.run_repeating(rotate_quotes, interval=3*24*3600)

    # перша рандомна цитата через 30 хв, далі ланцюжком
    jq.run_once(send_random_quote, when=30*60)

    # фіксовані нагадування
    jq.run_daily(remind_todo,     time(hour=7,  minute=30, tzinfo=TZ))
    jq.run_daily(remind_no_reels, time(hour=8,  minute=0,  tzinfo=TZ))
    jq.run_daily(remind_both,     time(hour=14, minute=0,  tzinfo=TZ))
    jq.run_daily(remind_bedtime,  time(hour=0,  minute=0,  tzinfo=TZ))

    # 3) Запускаємо polling у головному потоці
    app.run_polling()

if __name__ == "__main__":
    main()
