from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.menus import POSM_BUTTON_TEXT

router = Router()
POSM_USERS: set[int] = set()

@router.message(F.text == POSM_BUTTON_TEXT)
async def posm_enter(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    POSM_USERS.add(m.from_user.id)
    await m.answer("Детализация/экспорт в разработке.")
