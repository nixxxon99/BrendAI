from app.keyboards.menus import CATALOG_BUTTON_TEXT
# app/routers/catalog.py — интерактивный каталог
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.brands import fuzzy_suggest
from app.services.portfolio import in_portfolio, suggest_alternatives

router = Router()

CATALOG_USERS = {}


def kb_candidates(names):
    rows = [[InlineKeyboardButton(text=n, callback_data=f"brand:{n}")] for n in names]
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

@router.message(F.text == CATALOG_BUTTON_TEXT)
async def catalog_enter(m: Message):
    CATALOG_USERS[m.from_user.id] = True
    await m.answer("Напиши название бренда или категории — подскажу и покажу карточку из портфеля.")

@router.message(F.text, F.from_user.as_('u'))
async def catalog_query(m: Message, u):
    if not CATALOG_USERS.get(u.id):
        return
    q = (m.text or '').strip()
    if not q:
        return
    pairs = fuzzy_suggest(q, limit=10) or []
    names = [p[0] if isinstance(p, tuple) else str(p) for p in pairs][:10]
    if not names:
        await m.answer("Не нашёл подходящих брендов. Попробуй по-другому сформулировать.")
        return
    kb = kb_candidates(names)
    await m.answer("Нашёл похожее:", reply_markup=kb)

@router.callback_query(F.data.startswith("brand:"))
async def on_brand_tap(c: CallbackQuery):
    name = c.data.split(":", 1)[1]
    # Мини-карточка: наш/не наш + альтернатива
    if in_portfolio(name):
        alts = suggest_alternatives(name) or []
        msg = f"<b>{name}</b> — наш бренд.\nАльтернатива внутри портфеля: " + (', '.join(alts[:5]) if alts else 'нет данных')
    else:
        alts = suggest_alternatives(name) or []
        msg = f"<b>{name}</b> — не наш. Из портфеля можно предложить: " + (', '.join(alts[:5]) if alts else 'похожего нет')
    await c.message.answer(msg, parse_mode="HTML")
    await c.answer()
