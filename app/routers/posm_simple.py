# app/routers/posm_simple.py — простой заглушечный обработчик POSM
from aiogram import Router, F
from aiogram.types import Message

router = Router()

BTN_POSM = "📦 📦 POSM списание списание"
POSM_USERS = {}

@router.message(F.text == BTN_POSM)
async def posm_enter(m: Message):
    POSM_USERS[m.from_user.id] = True
    await m.answer("Введи параметры списания в одном сообщении (что / сколько / куда / кто). Пример: 'стойка 2 шт / бар Х / Иванов'.")

@router.message(F.text, F.from_user.as_('u'))
async def posm_text(m: Message, u):
    if not POSM_USERS.get(u.id):
        return
    txt = (m.text or '').strip()
    if not txt:
        return
    await m.answer("Принял заявку на списание:
" + txt + "
(Детализация/экспорт в разработке)")
