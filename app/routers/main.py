from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.menus import main_menu_kb

router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    await m.answer("Привет! Я BrendAI. Выбирай режим на клавиатуре ниже.", reply_markup=main_menu_kb())

@router.message(F.text.in_({"Старт","старт"}))
async def on_start_text(m: Message):
    await on_start(m)

@router.message(Command("menu"))
async def on_menu(m: Message):
    from app.utils.reset import reset_user
    reset_user(m.from_user.id)
    await m.answer("Меню:", reply_markup=main_menu_kb())

@router.message(Command("diag"))
async def on_diag(m: Message):
    try:
        from app.routers.ai_helper import AI_USERS
    except Exception:
        AI_USERS=set()
    try:
        from app.routers.vision import VISION_USERS
    except Exception:
        VISION_USERS=set()
    try:
        from app.routers.brands import CATALOG_USERS
    except Exception:
        CATALOG_USERS=set()
    await m.answer(f"DIAG:\nAI={m.from_user.id in AI_USERS}, Vision={m.from_user.id in VISION_USERS}, Catalog={m.from_user.id in CATALOG_USERS}")

@router.message(Command("ourcount"))
async def on_ourcount(m: Message):
    from app.services.ai_offline import _load_portfolio
    n = len(_load_portfolio())
    await m.answer(f"В портфеле: {n} наименований.")

@router.message(Command("ourbrands"))
async def on_ourbrands(m: Message):
    from app.services.ai_offline import _load_portfolio
    items = sorted(list(_load_portfolio()))
    if not items:
        await m.answer("Портфель пуст (data/portfolio.csv|json|txt не найден).")
        return
    head = items[:30]
    rest = len(items) - len(head)
    txt = "\n".join(f"• {x}" for x in head)
    if rest > 0:
        txt += f"\n… и ещё {rest}"
    await m.answer(txt)

@router.message(Command("reload_kb"))
async def on_reload_kb(m: Message):
    try:
        from app.services.ai_offline import reload_kb
        reload_kb()
        await m.answer("KB перезагружена.")
    except Exception as e:
        await m.answer(f"Не удалось перезагрузить KB: {e}")

@router.message(Command("branddiag"))
async def on_branddiag(m: Message):
    args = (m.text or "").split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Использование: /branddiag <запрос>")
        return
    from app.services.ai_offline import find_brand
    rec, cand = find_brand(args[1])
    if rec:
        await m.answer("MATCH: " + (rec.get("brand") or rec.get("name") or ""))
    elif cand:
        await m.answer("CANDIDATES:\n" + "\n".join("• " + x for x in cand))
    else:
        await m.answer("NO MATCH")

@router.message(Command("ocrdiag"))
async def on_ocrdiag(m: Message):
    from app.services.vision import last_ocr_text
    t = last_ocr_text() or "(пусто)"
    await m.answer("OCR:\n" + t[:2000])
