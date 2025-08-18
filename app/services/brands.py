# Minimal, robust brand service compatible with routers
import json, os, csv
from rapidfuzz import process, fuzz

def _load_catalog():
    p = os.path.join("data","catalog.json")
    try:
        js = json.load(open(p,"r",encoding="utf-8"))
        if isinstance(js, list):
            # support list of strings or dicts with "name"
            out = []
            for it in js:
                if isinstance(it, str): out.append(it)
                elif isinstance(it, dict): 
                    nm = it.get("name") or it.get("brand") or ""
                    if nm: out.append(nm)
            return out
        return []
    except Exception:
        return []

def _load_portfolio():
    p = os.path.join("data","portfolio.csv")
    rows = []
    if os.path.exists(p):
        try:
            r = csv.DictReader(open(p,"r",encoding="utf-8"), delimiter=";")
            col = None
            for h in (r.fieldnames or []):
                if h and "наимен" in h.lower(): col = h; break
            if col is None and r.fieldnames: col = r.fieldnames[0]
            for row in r:
                nm = (row.get(col) or "").strip()
                if nm: rows.append(nm)
        except Exception:
            pass
    return _dedup(rows)

def _load_kb_names():
    p = os.path.join("data","ingested_kb.json")
    arr = []
    if os.path.exists(p):
        try:
            js = json.load(open(p,"r",encoding="utf-8"))
            if isinstance(js, list):
                for it in js:
                    if isinstance(it, dict):
                        nm = (it.get("name") or it.get("brand") or "").strip()
                        if nm: arr.append(nm)
        except Exception:
            pass
    return _dedup(arr)

def _dedup(items):
    seen = set(); out=[]
    for x in items:
        k = x.lower()
        if k in seen: continue
        seen.add(k); out.append(x)
    return out

def _all_names():
    return _dedup(_load_catalog() + _load_portfolio() + _load_kb_names())

def suggest_candidates(needle: str, top_n: int = 15):
    names = _all_names()
    if not names: 
        return []
    hits = process.extract(needle or "", names, scorer=fuzz.WRatio, limit=top_n)
    return [h[0] for h in hits]

def brand_card(name: str):
    # Placeholder mini-card for now: in future can mark "наш/не наш" from KB/portfolio mapping
    return {"name": name, "is_ours": None, "alt": []}
