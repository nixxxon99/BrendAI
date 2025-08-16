# app/routers/main.py — старт и главное меню
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command

router = Router()

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📸 Фото-анализ"), KeyboardButton(text="🧠 AI эксперт")],
            [KeyboardButton(text="🔎 Каталог брендов"), KeyboardButton(text="📦 POSM списание")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Что сделать?"
    )

@router.message(CommandStart())
async def start(m: Message):
    await m.answer(
        "Привет! Я онлайн ✅\n"
        "• Пришли фото этикетки через «📸 Фото-анализ» — подберу наши альтернативы.\n"
        "• Или выбери действие из меню ниже.",
        reply_markup=main_menu_kb()
    )

@router.message(Command("version"))
async def version(m: Message):
    try:
        v = open("VERSION", "r", encoding="utf-8").read().strip()
    except Exception:
        v = "unknown"
    await m.answer(f"Версия бота: {v}")
