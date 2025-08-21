from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

AI_ENTRY_BUTTON_TEXT = "🧠 AI эксперт"
CATALOG_BUTTON_TEXT = "🔎 Каталог брендов"
VISION_BUTTON_TEXT = "📸 Фото-анализ"
POSM_BUTTON_TEXT = "📦 POSM списание"

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=AI_ENTRY_BUTTON_TEXT), KeyboardButton(text=CATALOG_BUTTON_TEXT)],
            [KeyboardButton(text=VISION_BUTTON_TEXT), KeyboardButton(text=POSM_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False,
        is_persistent=True
    )

def ai_exit_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Выйти из AI режима", callback_data="ai_exit")]])

def candidates_kb(names: list[str]) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=nm, callback_data="brand:" + nm)] for nm in names[:10]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
