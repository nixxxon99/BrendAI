# app/services/ai_offline.py
"""
Оффлайн-ядро 'AI эксперт' без внешних API.
- Матч брендов по каталогу и алиасам
- Проверка 'наш/не наш' по портфелю
- Загрузка локальной KB из data/kb/*.{md,txt,json}
- Подбор альтернатив из портфеля по категории/типу
- Общие советы по продажам, если бренд не распознан
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import os, json, re, glob

# --- lazy singletons ---
_CATALOG: List[dict] | None = None
_PORTFOLIO: set[str] | None = None
_KB: Dict[str, str] | None = None

def _load_catalog() -> List[dict]:
    global _CATALOG
    if _CATALOG is not None:
        return _CATALOG
    path_json = os.path.join("data", "catalog.json")
    if os.path.exists(path_json):
        try:
            data = json.load(open(path_json, "r", encoding="utf-8"))
            # файл может быть list или dict.values
            _CATALOG = list(data) if isinstance(data, list) else list(data.values())
        except Exception:
            _CATALOG = []
    else:
        _CATALOG = []
    return _CATALOG

def _load_portfolio() -> set[str]:
    global _PORTFOLIO
    if _PORTFOLIO is not None:
        return _PORTFOLIO
    # пытаемся взять из services.portfolio
    _PORTFOLIO = set()
    try:
        from app.services.portfolio import OUR_BRANDS
        _PORTFOLIO |= set(OUR_BRANDS)
    except Exception:
        pass
    # также читаем data/portfolio.json|txt (по строке на бренд)
    for p in [os.path.join("data","portfolio.json"), os.path.join("data","portfolio.txt")]:
        try:
            if os.path.exists(p):
                if p.endswith(".json"):
                    js = json.load(open(p,"r",encoding="utf-8"))
                    if isinstance(js, list): _PORTFOLIO |= set(map(str, js))
                else:
                    for line in open(p,"r",encoding="utf-8"):
                        t = line.strip()
                        if t: _PORTFOLIO.add(t)
        except Exception:
            pass
    return _PORTFOLIO

def _norm(s: str) -> str:
    return (s or "").strip()

def _brand_name(rec: dict) -> str:
    return _norm(rec.get("brand") or rec.get("name"))

def _brand_cat(rec: dict) -> str:
    return _norm(rec.get("category") or rec.get("type"))

def _load_kb() -> Dict[str, str]:
    "KB: brand -> concatenated text"
    global _KB
    if _KB is not None:
        return _KB
    _KB = {}
    kb_dir = os.path.join("data","kb")
    if not os.path.isdir(kb_dir):
        return _KB
    # json files
    for fp in glob.glob(os.path.join(kb_dir, "*.json")):
        try:
            js = json.load(open(fp,"r",encoding="utf-8"))
            if isinstance(js, dict):
                for k,v in js.items():
                    _KB[_norm(k)] = _KB.get(_norm(k), "") + "\n" + str(v)
        except Exception:
            pass
    # txt/md files
    for fp in glob.glob(os.path.join(kb_dir, "*.txt")) + glob.glob(os.path.join(kb_dir, "*.md")):
        try:
            name = os.path.splitext(os.path.basename(fp))[0]
            _KB[_norm(name)] = _KB.get(_norm(name), "") + "\n" + open(fp,"r",encoding="utf-8").read()
        except Exception:
            pass
    return _KB

def reload_kb():
    global _KB
    _KB = None
    _load_kb()

# --- brand matching ---
def _brand_index() -> Dict[str, dict]:
    idx = {}
    for rec in _load_catalog():
        nm = _brand_name(rec)
        if nm: idx[nm.casefold()] = rec
    return idx

def _aliases() -> Dict[str,str]:
    # пробуем взять из services.brands
    try:
        from app.services.brands import ALIASES
        al = {k.casefold(): v for k,v in ALIASES.items()}
    except Exception:
        al = {}
    return al

def find_brand(query: str) -> Tuple[Optional[dict], List[str]]:
    q = _norm(query)
    if not q:
        return None, []
    idx = _brand_index()
    # aliases
    al = _aliases()
    qlow = q.casefold()
    if qlow in al and al[qlow].casefold() in idx:
        return idx[al[qlow].casefold()], [al[qlow]]
    # exact
    if qlow in idx:
        nm = _brand_name(idx[qlow])
        return idx[qlow], [nm]
    # substring search
    hits = []
    for key, rec in idx.items():
        if qlow in key:
            hits.append(_brand_name(rec))
    # limit
    hits = sorted(set(hits))[:10]
    if hits:
        return None, hits
    return None, []

def in_portfolio(brand: str) -> bool:
    return _norm(brand) in _load_portfolio()

def _kb_text(brand: str) -> str:
    kb = _load_kb()
    # прямой ключ
    t = kb.get(_norm(brand))
    if t: return t.strip()
    # иногда имя файла без апострофов/доп слов
    key = re.sub(r"[^\w\s]+","", _norm(brand)).strip()
    return kb.get(key, "").strip()

def _alt_from_portfolio(category: str, exclude: str, limit: int = 3) -> List[str]:
    port = _load_portfolio()
    idx = _brand_index()
    alts = []
    for nm_cf, rec in idx.items():
        nm = _brand_name(rec)
        if nm == exclude: continue
        if nm in port and (_brand_cat(rec).casefold() == category.casefold() if category else True):
            alts.append(nm)
    # если по категории пусто — берём любые из портфеля
    if not alts:
        for nm_cf, rec in idx.items():
            nm = _brand_name(rec)
            if nm != exclude and nm in port:
                alts.append(nm)
    # уникальные, срез
    out = []
    for a in alts:
        if a not in out:
            out.append(a)
        if len(out) >= limit: break
    return out

def _generic_sales_tips(query: str) -> str:
    q = query.casefold()
    if "виски" in q or "whisky" in q or "whiskey" in q:
        return ("Как продавать виски:\n"
                "• Узнай предпочтения: дымность/сладость/регион.\n"
                "• Предложи дегустационный сет 2–3 позиций.\n"
                "• Подача: чистым, со льдом или хайболл 1:3.\n"
                "• Аргументы: происхождение, выдержка, стиль.")
    if "коньяк" in q or "cognac" in q:
        return ("Как продавать коньяк:\n"
                "• Уточни возраст/ценовой коридор.\n"
                "• Подчеркни мягкость и аромат (ваниль, сухофрукты).\n"
                "• Предложи тюльпановидный бокал, сервировка при 18–20°C.")
    return ("Как продавать алкоголь в целом:\n"
            "• Вопросы о вкусе/поводе/бюджете.\n"
            "• 2–3 релевантных варианта с короткими тезисами.\n"
            "• Упростить выбор: «я бы взял вот это — лучший баланс вкуса/цены».")

def format_answer(brand: Optional[str], status: Optional[bool], kb: str, alts: List[str]) -> str:
    lines = []
    if brand:
        lines.append(f"<b>Бренд:</b> {brand}")
    if status is not None:
        lines.append(f"<b>Статус:</b> {'наш ✅' if status else 'не наш ❌'}")
    if kb:
        lines.append(kb.strip())
    if alts:
        lines.append("<b>Альтернатива из портфеля:</b> " + ", ".join(alts))
    return "\n".join(lines).strip()

def answer_ai(query: str) -> str:
    """Основная точка входа AI-режима."""
    q = _norm(query)
    # 1) ищем бренд
    rec, candidates = find_brand(q)
    if rec:
        brand = _brand_name(rec)
        kb = _kb_text(brand)
        status = in_portfolio(brand)
        # если нет KB — соберём краткое описание из каталога
        if not kb:
            bits = []
            cat = _brand_cat(rec)
            country = rec.get("country")
            abv = rec.get("abv")
            if cat: bits.append(cat)
            if country: bits.append(country)
            if abv: bits.append(abv)
            if bits: kb = " / ".join(bits)
        # альтернатива если не наш
        alts = []
        if status is False:
            alts = _alt_from_portfolio(_brand_cat(rec), brand, limit=3)
        elif status is True:
            alts = []  # можно добавить 'соседние' из портфеля
        return format_answer(brand, status, kb, alts)

    # 2) если кандидаты — вернём список (пусть каталог отработает)
    if candidates:
        bullet = "\n".join("• " + c for c in candidates)
        return f"Нашёл бренды по запросу:\n{bullet}\n\nВыберите в меню «Каталог брендов» для карточки."

    # 3) общая консультация по категории
    return _generic_sales_tips(q)
