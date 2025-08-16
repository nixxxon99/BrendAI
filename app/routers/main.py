# main router: start + utils
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.menus import main_menu_kb
from app.routers.ai_helper import AI_USERS

router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
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

@router.message(Command("kb"))
async def on_kb(m: Message):
    await m.answer("Обновил клавиатуру.", reply_markup=main_menu_kb())

@router.message(Command("diag"))
async def on_diag(m: Message):
    # lazy imports to avoid cycles
    try:
        from app.services.portfolio import PORTFOLIO_COUNT
    except Exception:
        PORTFOLIO_COUNT = -1
    await m.answer(f"AI_USERS: {len(AI_USERS)}\nportfolio.csv: {PORTFOLIO_COUNT if PORTFOLIO_COUNT>=0 else 'нет'}")
