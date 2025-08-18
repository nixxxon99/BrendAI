# app/routers/posm_simple.py — простой обработчик POSM (демо)
from aiogram import Router, F
from aiogram.types import Message

router = Router()

BTN_POSM = "📦 POSM списание"
POSM_USERS: set[int] = set()

@router.message(F.text == BTN_POSM)
async def posm_enter(m: Message):
    POSM_USERS.add(m.from_user.id)
    await m.answer(
        "Введи параметры списания в одном сообщении (что / сколько / куда / кто).\n"
        "Пример: 'стойка 2 шт / Бар Х / Иванов'.\n"
        "Детализация/экспорт — в разработке."
    )

@router.message(lambda m: m.from_user and m.from_user.id in POSM_USERS and m.text)
async def posm_handle(m: Message):
    POSM_USERS.discard(m.from_user.id)
    # В боевой версии тут будет запись в CSV. Здесь — подтверждение.
    await m.answer("Принято. (Демо) Сохранил бы запись: " + m.text)
