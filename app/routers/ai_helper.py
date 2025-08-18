from app.keyboards.menus import AI_ENTRY_BUTTON_TEXT, CATALOG_BUTTON_TEXT, VISION_BUTTON_TEXT, POSM_BUTTON_TEXT, ai_exit_inline_kb

MENU_TEXTS = {AI_ENTRY_BUTTON_TEXT, CATALOG_BUTTON_TEXT, VISION_BUTTON_TEXT, POSM_BUTTON_TEXT}
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.keyboards.menus import AI_ENTRY_BUTTON_TEXT, ai_exit_inline_kb
from app.services.ai_offline import answer_ai

router = Router()
AI_USERS: set[int] = set()

@router.message(F.text.in_({AI_ENTRY_BUTTON_TEXT, 'AI эксперт', '🧠 AI эксперт'}))
async def ai_enter(m: Message):
    AI_USERS.add(m.from_user.id)
    await m.answer("AI-режим включён. Напиши вопрос про бренд/продажи. Для выхода — жми кнопку ниже.", reply_markup=ai_exit_inline_kb())

@router.callback_query(lambda c: c.data == "ai_exit")
async def ai_exit(c: CallbackQuery):
    AI_USERS.discard(c.from_user.id)
    await c.message.answer("AI-режим выключен.")
    await c.answer()

@router.message(lambda m: m.from_user and m.text and m.from_user.id in AI_USERS and m.text not in MENU_TEXTS)
async def ai_text(m: Message):
    txt = (m.text or "").strip()
    if not txt:
        return
    await m.answer(answer_ai(txt))
