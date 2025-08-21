import asyncio, os
from aiogram import Bot, Dispatcher
from app.bot import dp
async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env is not set")
    bot = Bot(token=token, parse_mode="HTML")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
