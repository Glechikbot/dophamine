import json
import random
import pytz
from datetime import time
from telegram.ext import Updater, JobQueue

# ===== Конфігурація =====
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
TZ = pytz.timezone("Europe/Kyiv")
# Скільки цитат тримати в quotes.json
ACTIVE_COUNT = 5

# ===== Функції =====
def load_quotes(path="quotes.json"):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def send_random_quote(context):
    quotes = load_quotes()
    text = f"💀 {random.choice(quotes)}"
    context.bot.send_message(chat_id=CHAT_ID, text=text)
    delay = random.randint(3600, 3 * 3600)
    context.job_queue.run_once(send_random_quote, delay)

def rotate_quotes(context):
    with open('master_quotes.json', 'r', encoding='utf-8') as f:
        master = json.load(f)
    new = random.sample(master, k=min(ACTIVE_COUNT, len(master)))
    with open('quotes.json', 'w', encoding='utf-8') as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
    print(f"[Quotes rotated] {len(new)} items")

def remind_todo(c): c.bot.send_message(chat_id=CHAT_ID, text="⏰ Пора перевірити свій список справ!")
def remind_no_reels(c): c.bot.send_message(chat_id=CHAT_ID, text="🚫 Не залипай у рілсах, вперед до справ!")
def remind_both(c):  c.bot.send_message(chat_id=CHAT_ID, text="🔃 Перевір справи та не забувай про рілси!")
def remind_bedtime(c): c.bot.send_message(chat_id=CHAT_ID, text="🌙 Час готуватися до сну. Вимикай екран, роби розтяжку.")

if __name__ == "__main__":
    updater = Updater(TOKEN)
    jq: JobQueue = updater.job_queue

    # Ротація цитат одразу й потім кожні 3 дні
    jq.run_once(rotate_quotes, when=0)
    jq.run_repeating(rotate_quotes, interval=3*24*3600)

    # Старт рандомних цитат через 30 хв, потім ланцюжком
    jq.run_once(send_random_quote, when=30*60)

    # Фіксовані сповіщення
    jq.run_daily(remind_todo,    time(hour=7, minute=30, tzinfo=TZ))
    jq.run_daily(remind_no_reels, time(hour=8, minute=0,  tzinfo=TZ))
    jq.run_daily(remind_both,    time(hour=14, minute=0, tzinfo=TZ))
    jq.run_daily(remind_bedtime, time(hour=0, minute=0,  tzinfo=TZ))

    updater.start_polling()
    updater.idle()
