from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.menus import CATALOG_BUTTON_TEXT
from app.services.brands import suggest_candidates, brand_card

router = Router()
CATALOG_USERS: set[int] = set()

@router.message(F.text.in_({CATALOG_BUTTON_TEXT, "Каталог брендов", "🔎 Каталог брендов"}))
async def catalog_enter(m: Message):
    CATALOG_USERS.add(m.from_user.id)
    await m.answer("Введи название бренда (или часть) — покажу кандидатов.")

@router.message(lambda m: m.text and m.from_user and m.from_user.id in CATALOG_USERS)
async def find(m: Message):
    q = (m.text or "").strip()
    if not q: 
        return
    items = suggest_candidates(q, top_n=15)
    if not items:
        await m.answer("Ничего не нашёл. Попробуй уточнить название.")
        return
    # простая выдача списком
    lines = ["Кандидаты:"]
    for it in items[:15]:
        lines.append("• " + str(it))
    await m.answer("\n".join(lines))


@router.message(lambda m: m.from_user and m.text and (m.from_user.id in CATALOG_USERS) and not m.text.startswith('/') and m.text not in {AI_ENTRY_BUTTON_TEXT, CATALOG_BUTTON_TEXT, VISION_BUTTON_TEXT, POSM_BUTTON_TEXT, "Назад", "🔙 Назад", "Назад ⬅️"})
async def catalog_query(m: Message):
    from app.services.brands import suggest_candidates, brand_card
    q = (m.text or "").strip()
    names = suggest_candidates(q, top_n=10) or []
    if not names:
        await m.answer("Ничего не нашёл. Попробуй уточнить название.")
        return
    # Покажем первую карточку, затем список кандидатов
    card = brand_card(names[0])
    if card:
        await m.answer(card, parse_mode="HTML")
    if len(names) > 1:
        await m.answer("Ещё варианты: " + ", ".join(names[1:5]))
