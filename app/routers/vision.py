from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.menus import VISION_BUTTON_TEXT

router = Router()
VISION_USERS: set[int] = set()

@router.message(F.text == VISION_BUTTON_TEXT)
async def vision_enter(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    VISION_USERS.add(m.from_user.id)
    await m.answer("Пришли фото бутылки/полки — распознаю надписи и предложу альтернативы, если не наш бренд.")

@router.message(lambda m: m.from_user and (m.from_user.id in VISION_USERS) and m.content_type == "photo")
async def vision_photo(m: Message):
    try:
        from app.services.vision import handle_photo_message
        await handle_photo_message(m)
    except Exception as e:
        print("[OCR ERROR]", e)
        await m.answer("OCR сервис недоступен. Попробуй позже.")

@router.message(lambda m: m.from_user and (m.from_user.id in VISION_USERS) and m.text is not None)
async def vision_text_hint(m: Message):
    await m.answer("Это режим фото. Пришли изображение или нажми /menu.")
