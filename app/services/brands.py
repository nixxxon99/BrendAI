from __future__ import annotations
from typing import List, Dict, Any, Optional
import json, os, re, unicodedata

ALIASES: Dict[str, str] = {
    "манки": "Monkey Shoulder",
    "манки шолдер": "Monkey Shoulder",
    "монки шолдер": "Monkey Shoulder",
    "баллантайнс": "Ballantine's",
    "балантайнс": "Ballantine's",
    "джемесон": "Jameson",
    "джеймесон": "Jameson",
    "джек": "Jack Daniel's",
    "гленфидих": "Glenfiddich",
}

try:
    from app.services.aliases_autogen import ALIASES_UPDATE
    ALIASES.update(ALIASES_UPDATE)
except Exception:
    pass

def _norm(s: str) -> str:
    return (s or "").strip()

def _strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))

_RU2EN = {
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"y",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f",
    "х":"h","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
}
def translit_ru_to_en(text: str) -> str:
    t = (text or "").lower()
    return "".join(_RU2EN.get(ch, ch) for ch in t)

_CATALOG_CACHE: Optional[list[dict]] = None
def _load_raw() -> list[dict]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    path_json = os.path.join("data", "catalog.json")
    if os.path.exists(path_json):
        try:
            data = json.load(open(path_json, "r", encoding="utf-8"))
            _CATALOG_CACHE = list(data) if isinstance(data, list) else list(data.values())
        except Exception:
            _CATALOG_CACHE = []
    else:
        _CATALOG_CACHE = []
    return _CATALOG_CACHE

def _index() -> list[tuple[str,str,str,dict]]:
    idx = []
    for rec in _load_raw():
        nm = _norm(rec.get("brand") or rec.get("name"))
        if not nm: 
            continue
        cf = _strip_accents(nm).casefold()
        tr = translit_ru_to_en(cf)
        idx.append((nm, cf, tr, rec))
    return idx

def exact_lookup(name: str) -> Optional[str]:
    if not name: return None
    low = _norm(name).casefold()
    if low in ALIASES:
        return ALIASES[low]
    for disp, cf, tr, rec in _index():
        if low == cf:
            return disp
    return None

def suggest_candidates(query: str, top_n: int = 10) -> list[str]:
    q = _norm(query)
    if not q: return []
    q_cf = _strip_accents(q).casefold()
    q_tr = translit_ru_to_en(q_cf)
    seeds = [q_cf, q_tr]
    if q_cf in ALIASES:
        seeds.append(_strip_accents(ALIASES[q_cf]).casefold())
    scores: Dict[str, float] = {}
    for disp, cf, tr, rec in _index():
        for s in seeds:
            if not s: continue
            score = 0.0
            if s in cf or s in tr: score += 3 + len(s)/max(1,len(cf))
            if cf.startswith(s) or tr.startswith(s): score += 1.5
            st = set(s.split()); ct = set(cf.split()); inter = len(st & ct)
            if inter: score += 2*inter
            if score>0:
                scores[disp] = max(scores.get(disp, 0.0), score)
    return [k for k,_ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))][:top_n]

def get_brand(name: str) -> Optional[dict]:
    nm = exact_lookup(name) or name
    for disp, cf, tr, rec in _index():
        if _norm(disp) == _norm(nm):
            return rec
    return None

def _kb_text(brand: str) -> str:
    base = os.path.join("data","kb")
    p = os.path.join(base, f"{brand}.md")
    if os.path.exists(p):
        return open(p,"r",encoding="utf-8").read()
    j = os.path.join(base, "kb.json")
    if os.path.exists(j):
        try:
            js = json.load(open(j,"r",encoding="utf-8"))
            return _norm(js.get(brand, ""))
        except Exception:
            pass
    return ""

def brand_card(name: str) -> Optional[str]:
    nm = exact_lookup(name) or name
    rec = get_brand(nm)
    if not rec:
        cand = suggest_candidates(nm, top_n=1)
        if cand:
            rec = get_brand(cand[0])
            nm = cand[0]
    if not rec:
        return None
    title = _norm(rec.get("brand") or rec.get("name") or nm)
    cat = _norm(rec.get("category") or rec.get("type"))
    country = _norm(rec.get("country"))
    abv = _norm(rec.get("abv"))
    kb = _kb_text(title)
    meta = " | ".join([x for x in [cat, country, abv] if x])
    lines = [f"<b>{title}</b>"]
    if meta: lines.append(meta)
    if kb: lines.append(kb.strip())
    return "\n".join(lines)
