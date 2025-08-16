# app/routers/main.py — старт, меню и обработка кнопок
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command

router = Router()

BTN_PHOTO   = "📸 Фото-анализ"
BTN_AI      = "🧠 AI эксперт"
BTN_CATALOG = "🔎 Каталог брендов"
BTN_POSM    = "📦 POSM списание"

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_PHOTO),   KeyboardButton(text=BTN_AI)],
            [KeyboardButton(text=BTN_CATALOG), KeyboardButton(text=BTN_POSM)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Что сделать?"
    )

@router.message(CommandStart())
async def start(m: Message):
    await m.answer(
        "Привет! Я онлайн ✅\n"
        "• Нажми «📸 Фото-анализ» и пришли фото этикетки — предложу наши альтернативы.\n"
        "• Или выбери действие из меню ниже.",
        reply_markup=main_menu_kb()
    )

@router.message(Command("version"))
async def version(m: Message):
    try:
        v = open("VERSION", "r", encoding="utf-8").read().strip()
    except Exception:
        v = "unknown"
    await m.answer(f"Версия бота: {v}")

@router.message(F.text == BTN_PHOTO)
async def on_photo_button(m: Message):
    await m.answer("Пришли **фото этикетки** как фото (не файл) — распознаю бренд и предложу нашу альтернативу.", parse_mode="Markdown")

@router.message(F.text == BTN_CATALOG)
async def on_catalog_button(m: Message):
    await m.answer("Напиши название бренда или категории — покажу карточку и наличие в портфеле.")

@router.message(F.text == BTN_AI)
async def on_ai_button(m: Message):
    await m.answer("Задай вопрос эксперту по алкоголю (бренды, категории, продажи, сравнения)." )

@router.message(F.text == BTN_POSM)
async def on_posm_button(m: Message):
    await m.answer("Отправь «/posm» или параметры списания (что/сколько/куда/кто) — сформирую запись и дам экспорт.")
