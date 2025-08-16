# main.py — чистый webhook для Aiogram v3 + Flask/Hypercorn
import os
import asyncio
import logging
from flask import Flask, request, Response, abort
from aiogram.types import Update

from app.bot import bot, dp
from app.settings import settings

app = Flask(__name__)

# Базовый URL сервиса и секрет
BASE_URL = (settings.webhook_url or "").rstrip("/")   # напр. https://brendai.onrender.com
SECRET    = settings.webhook_secret                   # строка без пробелов
WEBHOOK_PATH = f"/webhook/{SECRET}"
WEBHOOK_URL  = f"{BASE_URL}{WEBHOOK_PATH}" if BASE_URL else None

@app.get("/")
def root():
    return "BrendAI webhook OK", 200

@app.get("/_healthz")
def health():
    return "ok", 200

@app.post(WEBHOOK_PATH)
async def telegram_webhook() -> Response:
    # Доп. защита: проверим секретный заголовок Telegram
    if SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        return abort(403)

    update = Update.model_validate(await request.get_json())
    await dp.feed_update(bot, update)
    return Response(status=200)

async def main():
    logging.basicConfig(level=logging.INFO)

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL пуст. Для Worker-режима включайте polling, а здесь используем веб-хуки.")

    # Ставим вебхук (чистим старые апдейты)
    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=SECRET,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    print(f"✅ Webhook set: {WEBHOOK_URL}")

    # Запускаем Hypercorn и слушаем порт, который даёт Render
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    cfg = Config()
    cfg.bind = [f"0.0.0.0:{os.getenv('PORT', '10000')}"]  # Render прокинет $PORT
    await serve(app, cfg)

if __name__ == "__main__":
    asyncio.run(main())
