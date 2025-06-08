# Telegram Reminder Bot

## Опис
Цей бот робить автоматичні розсилки:
- Ранкове нагадування перевірити список справ (07:30).
- Нагадування «без рілс» о 08:00.
- Нагадування про справи + рілси о 14:00.
- Нагадування підготовки до сну о 00:00.
- Рандомні цитати Кастанеди (інтервал 1–3 години).
- Ротація активного списку цитат кожні 3 дні.

## Файли
- `bot.py` — основна логіка (polling + Flask health-check).
- `master_quotes.json` — повний набір цитат.
- `quotes.json` — активний набір цитат.
- `requirements.txt` — залежності.
- `.env` — змінні середовища (BOT_TOKEN, CHAT_ID, PORT).
- `Dockerfile` — для контейнера.
- `Procfile` — для Render/Heroku.
- `README.md` — ця інструкція.

## Налаштування
1. Встановіть змінні середовища (Render Dashboard):
   - `BOT_TOKEN` — ваш токен бота.
   - `CHAT_ID` — ваш Chat ID.
   - `PORT` — порт (наприклад, `8000` або автоматично отримає Render).
2. Деплойте на Render або Heroku як веб-сервіс.
3. Render автоматично виконає:
   ```
   pip install -r requirements.txt
   python bot.py
   ```
4. Health-check URL:
   ```
   https://<your-render-url>/
   ```

## Локальний запуск
```bash
pip install -r requirements.txt
export BOT_TOKEN=...
export CHAT_ID=...
export PORT=8000
python bot.py
```
