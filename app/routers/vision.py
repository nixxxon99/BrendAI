from app.keyboards.menus import VISION_BUTTON_TEXT
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.services.vision import recognize_brands_from_bytes
from app.services.brands import _kb_find
from app.services.portfolio import in_portfolio, suggest_alternatives
router = Router()
@router.message(F.text == VISION_BUTTON_TEXT)
async def info(m: Message):
    await m.answer("Пришли фото бутылки/полки — распознаю надписи и если это не наш бренд, предложу наши альтернативы.")
@router.message(F.photo)
async def handle_photo(m: Message):
    p = m.photo[-1]
    file = await m.bot.get_file(p.file_id)
    file_bytes = await m.bot.download_file(file.file_path)
    data = file_bytes.read()
    cands = recognize_brands_from_bytes(data)
    if not cands:
        await m.answer("Не смог распознать текст с фото. Попробуй более чёткий фронтальный кадр этикетки.")
        return
    for cand in cands[:10]:
        rec, disp = _kb_find(cand)
        if rec:
            await m.answer(f"Похоже на: <b>{disp}</b>", parse_mode="HTML")
            if not in_portfolio(disp):
                alts = suggest_alternatives(disp, maxn=5)
                if alts:
                    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"show:{a}")] for a in alts[:5]])
                    await m.answer("Это не наш бренд. Могу предложить альтернативы:", reply_markup=kb)
            return
    top = cands[0]
    if not in_portfolio(top):
        alts = suggest_alternatives(top, maxn=5)
        if alts:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"show:{a}")] for a in alts[:5]])
            await m.answer(f"Распознал(а): <b>{top}</b> — похоже, это не наш бренд. Вот наши альтернативы:", parse_mode="HTML", reply_markup=kb)
            return
    await m.answer("Посмотрел текст на фото, но не нашёл бренда в каталоге. Пришли название текстом — подберу альтернативы.")
