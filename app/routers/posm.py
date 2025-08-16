from app.keyboards.menus import POSM_BUTTON_TEXT
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import os, csv, datetime

router = Router()
POSM_FILE = "data/posm_log.csv"

def _kb_cancel():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Отмена")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

@router.message(F.text == POSM_BUTTON_TEXT)
async def posm_start(m: Message):
    m.bot.data.setdefault("posm_state", {})[m.from_user.id] = {"step": 1}
    await m.answer("Что списываем? (материал/позиция)", reply_markup=_kb_cancel())

@router.message(F.text == "Отмена")
async def posm_cancel(m: Message):
    m.bot.data.get("posm_state", {}).pop(m.from_user.id, None)
    await m.answer("Ок, отменил.", reply_markup=None)

@router.message(F.text.regexp(".+"))
async def posm_flow(m: Message):
    state = m.bot.data.get("posm_state", {}).get(m.from_user.id)
    if not state: return
    step = state.get("step", 1)
    if step == 1:
        state["item"] = m.text.strip(); state["step"]=2
        await m.answer("Сколько штук?"); return
    if step == 2:
        state["qty"] = m.text.strip(); state["step"]=3
        await m.answer("Название и адрес заведения?"); return
    if step == 3:
        state["venue"] = m.text.strip(); state["step"]=4
        await m.answer("Кто отдаёт? (ФИО)"); return
    if step == 4:
        state["giver"] = m.text.strip(); state["step"]=5
        await m.answer("Кто принял? (ФИО)"); return
    if step == 5:
        state["receiver"] = m.text.strip()
        os.makedirs("data", exist_ok=True)
        first = not os.path.exists(POSM_FILE)
        with open(POSM_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if first: w.writerow(["Дата","Материал","Шт","Заведение","Отправитель","Получатель"])
            w.writerow([datetime.date.today().isoformat(), state["item"], state["qty"], state["venue"], state["giver"], state["receiver"]])
        m.bot.data.get("posm_state", {}).pop(m.from_user.id, None)
        await m.answer("Списал ✅. Напиши /posm_export чтобы получить CSV.", reply_markup=None)

@router.message(F.text == "/posm_export")
async def posm_export(m: Message):
    if not os.path.exists(POSM_FILE):
        await m.answer("Ещё нет записей."); return
    await m.answer_document(FSInputFile(POSM_FILE), caption="POSM-лог")
