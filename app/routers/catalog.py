from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.menus import CATALOG_BUTTON_TEXT
from app.services.brands import fuzzy_suggest  # alias to suggest_candidates

router = Router()
CATALOG_USERS: set[int] = set()

@router.message(F.text.in_({CATALOG_BUTTON_TEXT, "Каталог брендов", "🔎 Каталог брендов"}))
async def catalog_enter(m: Message):
    CATALOG_USERS.add(m.from_user.id)
    await m.answer("Введи название бренда (или часть) — покажу кандидатов.")

@router.message(lambda m: m.text and m.from_user and m.from_user.id in CATALOG_USERS)
async def catalog_query(m: Message):
    q = (m.text or "").strip()
    if not q:
        return
    items = fuzzy_suggest(q, top_n=15)
    if not items:
        await m.answer("Ничего не нашёл. Попробуй уточнить название.")
        return
    lines = ["Кандидаты:"] + [f"• {it}" for it in items[:15]]
    await m.answer("\n".join(lines))
