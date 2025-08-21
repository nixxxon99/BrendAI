from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.keyboards.menus import CATALOG_BUTTON_TEXT, candidates_kb

router = Router()
CATALOG_USERS: set[int] = set()

@router.message(F.text == CATALOG_BUTTON_TEXT)
async def open_catalog(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    CATALOG_USERS.add(m.from_user.id)
    await m.answer("Введи название бренда (или часть) — покажу кандидатов.")

@router.message(lambda m: m.from_user and m.text and (m.from_user.id in CATALOG_USERS) and not m.text.startswith("/") and m.text not in {"🧠 AI эксперт", "🔎 Каталог брендов", "📸 Фото-анализ", "📦 POSM списание", "Назад", "🔙 Назад", "Назад ⬅️"})
async def catalog_query(m: Message):
    from app.services.brands import suggest_candidates, brand_card, exact_lookup, get_brand
    q = (m.text or "").strip()
    canon = exact_lookup(q) or q
    if get_brand(canon):
        card = brand_card(canon)
        if card:
            await m.answer(card, parse_mode="HTML")
            return
    names = suggest_candidates(q, top_n=10) or []
    if not names:
        await m.answer("Ничего не нашёл. Попробуй уточнить название.")
        return
    if len(names) == 1:
        card = brand_card(names[0])
        if card:
            await m.answer(card, parse_mode="HTML")
            return
    await m.answer("Кандидаты:", reply_markup=candidates_kb(names))

@router.callback_query(lambda c: c.data and c.data.startswith("brand:"))
async def catalog_pick(c: CallbackQuery):
    from app.services.brands import brand_card
    name = c.data.split(":", 1)[1]
    card = brand_card(name)
    if not card:
        await c.answer("Карточка не найдена", show_alert=False)
        return
    await c.message.answer(card, parse_mode="HTML")
    await c.answer()
