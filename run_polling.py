
import asyncio, os
from aiogram import Bot, Dispatcher
from app.routers import main as main_router
from app.routers import ai_helper, catalog, brands, vision, posm_simple

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("API_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(main_router.router)
    for r in (ai_helper.router, catalog.router if hasattr(catalog, "router") else brands.router, vision.router, posm_simple.router):
        dp.include_router(r)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
