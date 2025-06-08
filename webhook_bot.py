import os
import json
import random
import pytz
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, JobQueue

# ===== Конфігурація через ENV =====
TOKEN       = os.environ["BOT_TOKEN"]
CHAT_ID     = os.environ["CHAT_ID"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # e.g. https://dophamine.onrender.com
PORT        = int(os.environ.get("PORT", 8443))
TZ          = pytz.timezone("Europe/Kyiv")
ACTIVE_COUNT = 5

# ===== Функція для загрузки цитат =====
def load_quotes(path="quotes.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===== Job-функції =====
async def send_random_quote(ctx: ContextTypes.DEFAULT_TYPE):
    quotes = load_quotes()
    text = f"💀 {random.choice(quotes)}"
    await ctx.bot.send_message(chat_id=CHAT_ID, text=text)
    # Запланувати наступну цитату через 1–3 години
    delay = random.randint(3600, 3 * 3600)
    ctx.job_queue.run_once(send_random_quote, delay)

async def rotate_quotes(ctx: ContextTypes.DEFAULT_TYPE):
    with open("master_quotes.json", "r", encoding="utf-8") as f:
        master = json.load(f)
    new = random.sample(master, k=min(ACTIVE_COUNT, len(master)))
    with open("quotes.json", "w", encoding="utf-8") as f:
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

async def ping(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот працює через вебхук!")

# ===== Запуск бота через webhook =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    jq: JobQueue = app.job_queue

    # Додати обробник /ping
    app.add_handler(CommandHandler("ping", ping))

    # Ротація цитат: одразу та кожні 3 дні
    jq.run_once(rotate_quotes, when=0)
    jq.run_repeating(rotate_quotes, interval=3 * 24 * 3600)

    # Рандомні цитати: перша через 30 хв, далі ланцюжком
    jq.run_once(send_random_quote, when=30 * 60)

    # Фіксовані нагадування
    jq.run_daily(remind_todo,     time(hour=7,  minute=30, tzinfo=TZ))
    jq.run_daily(remind_no_reels, time(hour=8,  minute=0,  tzinfo=TZ))
    jq.run_daily(remind_both,     time(hour=14, minute=0,  tzinfo=TZ))
    jq.run_daily(remind_bedtime,  time(hour=0,  minute=0,  tzinfo=TZ))

    # Налаштувати webhook
    path = f"/{TOKEN}"
    app.bot.set_webhook(f"{WEBHOOK_URL}{path}")

    # Запуск HTTP-сервера для Telegram webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN
    )
