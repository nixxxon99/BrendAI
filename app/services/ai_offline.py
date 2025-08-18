# Offline AI helper
import os, json, csv
from rapidfuzz import process, fuzz

def _load_kb():
    p = os.path.join("data","ingested_kb.json")
    if os.path.exists(p):
        try:
            js = json.load(open(p,"r",encoding="utf-8"))
            if isinstance(js, list): return js
        except Exception: pass
    return []

def _name(it):
    return (it.get("name") or it.get("brand") or "").strip() if isinstance(it, dict) else ""

def _load_portfolio_names():
    p = os.path.join("data","portfolio.csv")
    names = []
    if os.path.exists(p):
        try:
            r = csv.DictReader(open(p,"r",encoding="utf-8"), delimiter=";")
            col = None
            for h in (r.fieldnames or []):
                if h and "наимен" in h.lower(): col = h; break
            if col is None and r.fieldnames: col = r.fieldnames[0]
            for row in r:
                nm = (row.get(col) or "").strip()
                if nm: names.append(nm)
        except Exception: pass
    # dedup keep order
    seen = set(); out=[]
    for n in names:
        k=n.lower()
        if k in seen: continue
        seen.add(k); out.append(n)
    return out

def _alts(brand, limit=5):
    names = _load_portfolio_names()
    if not names: return []
    hits = process.extract(brand, names, scorer=fuzz.token_sort_ratio, limit=limit)
    return [h[0] for h in hits if isinstance(h,(list,tuple))]

def answer_ai(q: str) -> str:
    kb = _load_kb()
    if not kb:
        return "Оффлайн-БЗ отсутствует. Добавь data/ingested_kb.json и перезапусти."
    names = [_name(x) for x in kb if _name(x)]
    best = process.extractOne(q, names, scorer=fuzz.WRatio)
    if not best:
        return "Не нашёл бренд в оффлайн-БЗ. Уточни название."
    brand = best[0]
    item = next((it for it in kb if _name(it)==brand), {})
    is_ours = item.get("is_ours")
    pitch = item.get("pitch") or "Сфокусируйся на вкусе/простых подачах/прибыли на бокал."
    hint  = item.get("alternatives_hint") or ""
    alts = _alts(brand, 5)
    lines = [f"Бренд: {brand}"]
    lines.append("Статус: наш ✅" if is_ours else "Статус: не наш ❌" if is_ours is False else "Статус: не указан")
    lines.append("Как продавать: " + pitch)
    if hint: lines.append(hint)
    if alts:
        lines.append(("Смежные позиции" if is_ours else "Наши альтернативы") + ": " + "; ".join(alts))
    return "\n".join(lines)
