# main.py — веб-хуки на aiohttp для Aiogram v3 (Render Web Service)
import os
import logging
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.bot import bot, dp
from app.utils.gcv_bootstrap import ensure_gcv_credentials
from app.settings import settings

logging.basicConfig(level=logging.INFO)

BASE_URL = (settings.webhook_url or "").rstrip("/")   # напр. https://<name>.onrender.com
SECRET   = settings.webhook_secret                    # <-- ENV: WEBHOOK_SECRET
WEBHOOK_PATH = f"/webhook/{SECRET}"
WEBHOOK_URL  = f"{BASE_URL}{WEBHOOK_PATH}" if BASE_URL else ""

async def root(_):
    return web.Response(text="BrendAI webhook OK")

async def health(_):
    return web.Response(text="ok")

async def on_startup(app: web.Application):
    ensure_gcv_credentials()
    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL пуст. Задай ENV WEBHOOK_URL = https://<name>.onrender.com")
    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=SECRET,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    print(f"✅ Webhook set: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

def create_app() -> web.Application:
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=SECRET).register(app, path=WEBHOOK_PATH)
    app.router.add_get("/", root)
    app.router.add_get("/_healthz", health)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
