import os, asyncio
from aiogram.types import Message
from app.keyboards.menus import candidates_kb
import io
from PIL import Image
import numpy as np

_LAST_OCR_TEXT = ""

def last_ocr_text():
    return _LAST_OCR_TEXT

async def _download_best_photo(m: Message) -> bytes:
    bot = m.bot
    sizes = m.photo
    if not sizes:
        return b""
    best = sizes[-1]
    file = await bot.get_file(best.file_id)
    return await bot.download_file(file.file_path)

def _preprocess(img: Image.Image) -> Image.Image:
    if max(img.size) < 1280:
        scale = 1280 / max(img.size)
        img = img.resize((int(img.width*scale), int(img.height*scale)))
    return img

def _ocr_pytesseract(img: Image.Image, langs: str = "rus+eng") -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(img, lang=langs) or ""
    except Exception as e:
        return ""

def _ocr_easyocr(np_img) -> str:
    try:
        import easyocr
        langs = os.environ.get("OCR_LANGS","ru,en").split(",")
        reader = easyocr.Reader(langs, gpu=False)
        res = reader.readtext(np_img)
        parts = [t[1] for t in res if len(t)>=2]
        return "\n".join(parts)
    except Exception as e:
        return ""

async def handle_photo_message(m: Message):
    global _LAST_OCR_TEXT
    bin_data = await _download_best_photo(m)
    if not bin_data:
        await m.answer("Не удалось скачать фото.")
        return
    img = Image.open(io.BytesIO(bin_data)).convert("RGB")
    img = _preprocess(img)
    text = ""
    prov = os.environ.get("OCR_PROVIDER","easyocr")
    if prov == "tesseract":
        text = _ocr_pytesseract(img, os.environ.get("OCR_LANGS","rus+eng"))
    else:
        text = _ocr_easyocr(np.array(img))
        if not text:
            text = _ocr_pytesseract(img, os.environ.get("OCR_LANGS","rus+eng"))
    _LAST_OCR_TEXT = text or ""
    from app.services.ai_offline import find_brand
    rec, cand = find_brand(text or "")
    if rec:
        name = (rec.get("brand") or rec.get("name") or "").strip()
        from app.services.brands import brand_card
        card = brand_card(name)
        if card:
            await m.answer(card, parse_mode="HTML")
            return
    if cand:
        await m.answer("Нашёл варианты по фото:", reply_markup=candidates_kb(cand))
        return
    await m.answer("Не распознал бренд на фото. Попробуйте сделать кадр ближе/резче или введите название текстом.")
