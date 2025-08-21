from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import os, json, re, glob, csv

_CATALOG = None
_PORTFOLIO = None
_KB = None

def _norm(s: str) -> str:
    return (s or "").strip()

def _load_catalog() -> List[dict]:
    global _CATALOG
    if _CATALOG is not None:
        return _CATALOG
    path_json = os.path.join("data", "catalog.json")
    if os.path.exists(path_json):
        try:
            data = json.load(open(path_json, "r", encoding="utf-8"))
            _CATALOG = list(data) if isinstance(data, list) else list(data.values())
        except Exception:
            _CATALOG = []
    else:
        _CATALOG = []
    return _CATALOG

def _brand_name(rec: dict) -> str:
    return _norm(rec.get("brand") or rec.get("name"))

def _brand_cat(rec: dict) -> str:
    return _norm(rec.get("category") or rec.get("type"))

def _brand_index() -> Dict[str, dict]:
    return {(_brand_name(r) or "").casefold(): r for r in _load_catalog() if _brand_name(r)}

def _load_portfolio() -> set[str]:
    global _PORTFOLIO
    if _PORTFOLIO is not None:
        return _PORTFOLIO
    _PORTFOLIO = set()
    try:
        from app.services.portfolio import OUR_BRANDS
        _PORTFOLIO |= set(map(str, OUR_BRANDS))
    except Exception:
        pass
    for p in [os.path.join("data","portfolio.json"), os.path.join("data","portfolio.txt"), os.path.join("data","portfolio.csv")]:
        if not os.path.exists(p): continue
        try:
            if p.endswith(".json"):
                js = json.load(open(p,"r",encoding="utf-8"))
                if isinstance(js, list):
                    for v in js:
                        name = (str(v) if v is not None else "").strip()
                        if name: _PORTFOLIO.add(name)
                elif isinstance(js, dict):
                    for k in js.keys():
                        name = (str(k) if k is not None else "").strip()
                        if name: _PORTFOLIO.add(name)
            elif p.endswith(".txt"):
                for line in open(p,"r",encoding="utf-8"):
                    name = (line or "").strip()
                    if name: _PORTFOLIO.add(name)
            elif p.endswith(".csv"):
                with open(p,"r",encoding="utf-8",errors="ignore") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row: continue
                        name = (row[0] or "").strip()
                        if not name: continue
                        if name.lower() in {"brand","name","бренд"}: continue
                        _PORTFOLIO.add(name)
        except Exception:
            pass
    return _PORTFOLIO

def in_portfolio(brand: str) -> bool:
    return _norm(brand) in _load_portfolio()

def _load_kb() -> Dict[str, str]:
    global _KB
    if _KB is not None:
        return _KB
    _KB = {}
    kb_dir = os.path.join("data","kb")
    if not os.path.isdir(kb_dir):
        return _KB
    for fp in glob.glob(os.path.join(kb_dir, "*.json")):
        try:
            js = json.load(open(fp,"r",encoding="utf-8"))
            if isinstance(js, dict):
                for k,v in js.items():
                    _KB[_norm(k)] = _KB.get(_norm(k), "") + "\n" + str(v)
        except Exception:
            pass
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

def _aliases() -> Dict[str,str]:
    try:
        from app.services.brands import ALIASES
        return {k.casefold(): v for k,v in ALIASES.items()}
    except Exception:
        return {}

def find_brand(query: str):
    q = _norm(query)
    if not q:
        return None, []
    qlow = q.casefold()
    for trig in ["как продавать", "как продать", "как предложить", "как продвигать", "альтернатива"]:
        if trig in qlow:
            qlow = qlow.split(trig,1)[1].strip() or qlow
    idx = _brand_index()
    al = _aliases()
    if qlow in al and al[qlow].casefold() in idx:
        nm = al[qlow]
        return idx[nm.casefold()], [nm]
    if qlow in idx:
        nm = _brand_name(idx[qlow])
        return idx[qlow], [nm]
    names = []
    try:
        from app.services.brands import suggest_candidates
        names = suggest_candidates(qlow, top_n=10)
    except Exception:
        pass
    if names:
        if len(names) == 1 and names[0].casefold() in idx:
            return idx[names[0].casefold()], [names[0]]
        for n in names:
            if n.casefold() in idx:
                return idx[n.casefold()], [n]
        return None, names
    hits = []
    for key, rec in idx.items():
        if qlow in key:
            hits.append(_brand_name(rec))
    hits = sorted(set(hits))[:10]
    if hits:
        if len(hits) == 1 and hits[0].casefold() in idx:
            return idx[hits[0].casefold()], [hits[0]]
        return None, hits
    return None, []

def _kb_text(brand: str) -> str:
    kb = _load_kb()
    return kb.get(_norm(brand), "").strip()

def _alt_from_portfolio(category: str, exclude: str, limit: int = 3) -> List[str]:
    port = _load_portfolio()
    idx = _brand_index()
    alts = []
    for nm_cf, rec in idx.items():
        nm = _brand_name(rec)
        if nm == exclude: continue
        if nm in port and ((category or "").casefold() == (_brand_cat(rec) or "").casefold() if category else True):
            alts.append(nm)
    if not alts:
        for nm_cf, rec in idx.items():
            nm = _brand_name(rec)
            if nm != exclude and nm in port:
                alts.append(nm)
    out = []
    for a in alts:
        if a not in out:
            out.append(a)
        if len(out) >= limit: break
    return out

def _generic_sales_tips(query: str) -> str:
    q = query.casefold()
    if "виски" in q or "whisk" in q:
        return ("Как продавать виски:\n"
                "• Уточни профиль: дым/сладость/регион.\n"
                "• Предложи 2–3 дегустационных варианта.\n"
                "• Подача: чистым/со льдом/хайболл 1:3.\n"
                "• Аргументы: происхождение, выдержка, стиль.")
    if "коньяк" in q or "cognac" in q:
        return ("Как продавать коньяк:\n"
                "• Возраст/категория и бюджет.\n"
                "• Подчеркни мягкость и аромат.\n"
                "• Подача при 18–20°C, тюльпановидный бокал.")
    return ("Как продавать алкоголь:\n"
            "• Выясни вкус/повод/бюджет.\n"
            "• Дай 2–3 релевантных опции.\n"
            "• Упростить выбор: «это лучший баланс вкуса/цены».")

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
    q = _norm(query)
    rec, candidates = find_brand(q)
    if rec:
        brand = _brand_name(rec)
        kb = _kb_text(brand)
        status = in_portfolio(brand)
        cat = _brand_cat(rec)
        if not kb:
            kb = _generic_sales_tips(cat or q)
        alts = []
        if status is False:
            alts = _alt_from_portfolio(cat, brand, limit=3)
        return format_answer(brand, status, kb, alts)

    if candidates:
        bullet = "\n".join("• " + c for c in candidates)
        return f"Нашёл бренды по запросу:\n{bullet}\n\nОткрой «Каталог брендов» для карточки."

    return _generic_sales_tips(q)
