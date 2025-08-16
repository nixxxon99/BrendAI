# app/routers/main.py — старт и общее меню
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.menus import main_menu_kb

router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
    await m.answer(
        "Привет! Я BrendAI. Выбирай режим на клавиатуре ниже.",
        reply_markup=main_menu_kb()
    )

@router.message(Command("version"))
async def on_version(m: Message):
    try:
        with open("VERSION", "r", encoding="utf-8") as f:
            v = f.read().strip()
    except Exception:
        v = "unknown"
    await m.answer(v)
