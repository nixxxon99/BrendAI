# main.py
import os
import asyncio
from flask import Flask, request, Response
from aiogram.types import Update

from app.settings import settings
from app.bot import bot, dp

WEBHOOK_PATH = f"/webhook/{settings.webhook_secret}"
WEBHOOK_URL = (settings.webhook_url + WEBHOOK_PATH) if settings.webhook_url else ""

app = Flask(__name__)

@app.post(WEBHOOK_PATH)
async def webhook() -> Response:
    update = Update.model_validate(await request.get_json())
    await dp.feed_update(bot, update)
    return Response(status=200)

async def run_webhook():
    import hypercorn.asyncio, hypercorn.config
    cfg = hypercorn.config.Config()
    # для Web Service на Render:
    cfg.bind = [f"0.0.0.0:{os.getenv('PORT', '10000')}"]
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")
    await hypercorn.asyncio.serve(app, cfg)

async def run_polling():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🔄 WEBHOOK_URL не задан — запускаю long-polling")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

async def main():
    if WEBHOOK_URL:
        await run_webhook()
    else:
        await run_polling()

if __name__ == "__main__":
    asyncio.run(main())
