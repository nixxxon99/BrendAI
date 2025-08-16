# app/routers/posm_simple.py — простой обработчик POSM (заглушка)
from aiogram import Router, F
from aiogram.types import Message
try:
    from app.keyboards.menus import POSM_BUTTON_TEXT as BTN_POSM
except Exception:
    BTN_POSM = "📦 POSM списание"

router = Router()
POSM_USERS = set()

@router.message(F.text == BTN_POSM)
async def posm_enter(m: Message):
    POSM_USERS.add(m.from_user.id)
    await m.answer(
        "Введи параметры списания в одной строке: что / сколько / куда / кто.\n"
        "Пример: стойка 2 / Бар Х / Иванов"
    )

@router.message(lambda m: m.text is not None and m.from_user and m.from_user.id in POSM_USERS)
async def posm_text(m: Message):
    if m.from_user.id not in POSM_USERS:
        return
    txt = (m.text or "").strip()
    if not txt:
        return
    POSM_USERS.discard(m.from_user.id)
    await m.answer(
        f"Принял заявку на списание:\n{txt}\n\nДетализация/экспорт в разработке."
    )
