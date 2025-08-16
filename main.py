# main.py — чистый webhook для Aiogram v3 + Flask/Hypercorn
import os
import asyncio
import logging
from flask import Flask, request, Response, abort
from aiogram.types import Update

from app.bot import bot, dp
from app.settings import settings

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Базовый URL твоего Web Service на Render и секрет
# WEBHOOK_URL и WEBHOOK_SECRET читаются из окружения через app/settings.py
BASE_URL = (settings.webhook_url or "").rstrip("/")    # напр. https://brendai.onrender.com
SECRET   = settings.webhook_secret                     # строка без пробелов
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
    # Защита: Telegram пришлёт заголовок с тем же секретом
    if SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        return abort(403)

    # ВАЖНО: во Flask get_json() синхронный — без await
    data = request.get_json(silent=True, force=True) or {}
    update = Update.model_validate(data)

    await dp.feed_update(bot, update)
    return Response(status=200)

async def main():
    if not WEBHOOK_URL:
        raise RuntimeError(
            "WEBHOOK_URL пуст. Для веб-хуков нужен Web Service и валидный URL "
            "(например, https://<имя>.onrender.com)."
        )

    # Ставим вебхук и очищаем старые апдейты
    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=SECRET,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    print(f"✅ Webhook set: {WEBHOOK_URL}")

    # Render прокидывает порт в $PORT — слушаем его
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    cfg = Config()
    cfg.bind = [f"0.0.0.0:{os.getenv('PORT', '10000')}"]
    await serve(app, cfg)

if __name__ == "__main__":
    asyncio.run(main())
