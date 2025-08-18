from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.menus import main_menu_kb
from app.routers.ai_helper import AI_USERS

router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    await m.answer("Привет! Я BrendAI. Выбирай режим на клавиатуре ниже.", reply_markup=main_menu_kb())

@router.message(Command("version"))
async def on_version(m: Message):
    try:
        with open("VERSION","r",encoding="utf-8") as f: v=f.read().strip()
    except Exception: v="unknown"
    await m.answer(v)

@router.message(Command("ping"))
async def on_ping(m: Message):
    await m.answer("pong")

@router.message(Command("mode_off"))
async def on_mode_off(m: Message):
    AI_USERS.discard(m.from_user.id)
    await m.answer("Режимы выключены. Нажмите кнопку на клавиатуре, чтобы войти заново.", reply_markup=main_menu_kb())


@router.message(Command("menu"))
async def on_menu(m: Message):
    from app.keyboards.menus import main_menu_kb
    await m.answer("Меню:", reply_markup=main_menu_kb())
