# app/routers/main.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.menus import main_menu_kb

router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
    # Полный сброс режимов и показ меню
    try:
        from app.utils.reset import reset_user
        reset_user(m.from_user.id)
    except Exception:
        pass
    await m.answer("Привет! Я BrendAI. Выбирай режим на клавиатуре ниже.", reply_markup=main_menu_kb())

# Дубликат команды — на всякий случай (если юзер отправляет 'Старт' текстом)
@router.message(F.text.in_(('Старт', 'старт')))
async def on_start_text(m: Message):
    await on_start(m)

@router.message(Command("menu"))
async def on_menu(m: Message):
    try:
        from app.utils.reset import reset_user
        reset_user(m.from_user.id)
    except Exception:
        pass
    await m.answer("Меню:", reply_markup=main_menu_kb())

# Пинг для проверки живости
@router.message(Command("ping"))
async def on_ping(m: Message):
    await m.answer("pong")
