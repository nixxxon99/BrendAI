# app/routers/main.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.menus import main_menu_kb

router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    await m.answer("Привет! Я BrendAI. Выбирай режим на клавиатуре ниже.", reply_markup=main_menu_kb())

@router.message(F.text.in_({"Старт","старт"}))
async def on_start_text(m: Message):
    await on_start(m)

@router.message(Command("menu"))
async def on_menu(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    await m.answer("Меню:", reply_markup=main_menu_kb())

@router.message(Command("ping"))
async def on_ping(m: Message):
    await m.answer("pong")

@router.message(Command("diag"))
async def on_diag(m: Message):
    try:
        from app.routers.ai_helper import AI_USERS
    except Exception:
        AI_USERS=set()
    try:
        from app.routers.vision import VISION_USERS
    except Exception:
        VISION_USERS=set()
    try:
        from app.routers.brands import CATALOG_USERS
    except Exception:
        CATALOG_USERS=set()
    await m.answer(f"DIAG:\nAI={m.from_user.id in AI_USERS}, Vision={m.from_user.id in VISION_USERS}, Catalog={m.from_user.id in CATALOG_USERS}")


@router.message(Command("reload_kb"))
async def on_reload_kb(m: Message):
    try:
        from app.services.ai_offline import reload_kb
        reload_kb()
        await m.answer("KB перезагружена.")
    except Exception as e:
        await m.answer(f"Не удалось перезагрузить KB: {e}")
