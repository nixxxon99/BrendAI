# app/services/brands.py
# Поддержка JSON в виде СПИСКА карточек [{...}, {...}] или словаря {name: {...}}
import json, re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher

# Где искать базу
SOURCE_FILES = [Path("data/catalog.json"), Path("data/brands_kb.json")]

# ---------- загрузка базы ----------
def _load_raw() -> List[Dict[str, Any]]:
    for p in SOURCE_FILES:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                items: List[Dict[str, Any]] = []
                for k, v in data.items():
                    if isinstance(v, dict):
                        d = dict(v)
                        d.setdefault("brand", k)
                        items.append(d)
                print(f"[brands] Loaded {len(items)} items from {p} (dict)")
                return items
            elif isinstance(data, list):
                items = [x for x in data if isinstance(x, dict)]
                print(f"[brands] Loaded {len(items)} items from {p} (list)")
                return items
            else:
                print(f"[brands] Unsupported JSON root in {p}: {type(data)}")
                return []
    print("[brands] No data file found")
    return []

RAW: List[Dict[str, Any]] = _load_raw()

# ---------- нормализация ----------
def _norm_keep_numbers(s: str) -> str:
    """Нормализация с сохранением цифр (нужна для алиасов с 12/14/18 и т.п.)."""
    s = (s or "").lower().strip()
    s = s.replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    # убираем только объёмы/единицы, а ЦИФРЫ возраста оставляем
    s = re.sub(r"\b(\d+[.,]?\d*)\s*(l|л|литр(а|ов)?|ml|мл)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _norm(s: str) -> str:
    """Базовая нормализация (без цифр). Подходит для каноничных имен и свободного ввода."""
    s = _norm_keep_numbers(s)
    # убрать «голые» числа (0.7, 12 и т.д.)
    s = re.sub(r"\b(0\.\d+|[1-9]\d*)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ---------- индексация ----------
NAME_INDEX: Dict[str, Dict[str, Any]] = {}   # norm(бренд без цифр) -> запись
ALIASES_NUM: Dict[str, str] = {}             # norm_keep_numbers(алиас) -> канон. имя бренда (с цифрами!)
ALIASES: Dict[str, str] = {}                 # norm(алиас без цифр) -> канон. имя бренда
ALL_CANON: List[str] = []                    # список каноничных имён

# Корневые алиасы (короткие запросы одним словом)
ROOT_ALIASES: Dict[str, str] = {
    _norm_keep_numbers("грантс"): "Grant's Triple Wood",
    _norm_keep_numbers("grant's"): "Grant's Triple Wood",
    _norm_keep_numbers("grants"): "Grant's Triple Wood",

    _norm_keep_numbers("тулламор"): "Tullamore D.E.W. Original",
    _norm_keep_numbers("tullamore"): "Tullamore D.E.W. Original",

    _norm_keep_numbers("гленфиддик"): "Glenfiddich 12 Year Old",
    _norm_keep_numbers("glenfiddich"): "Glenfiddich 12 Year Old",

    _norm_keep_numbers("балвени"): "The Balvenie 12 Year Old DoubleWood",
    _norm_keep_numbers("balvenie"): "The Balvenie 12 Year Old DoubleWood",

    _norm_keep_numbers("монки"): "Monkey Shoulder Blended Malt",
    _norm_keep_numbers("шолдер"): "Monkey Shoulder Blended Malt",
    _norm_keep_numbers("monkey shoulder"): "Monkey Shoulder Blended Malt",

    _norm_keep_numbers("хендрикс"): "Hendrick's Gin",
    _norm_keep_numbers("hendricks"): "Hendrick's Gin",
    _norm_keep_numbers("hendrick's"): "Hendrick's Gin",

    _norm_keep_numbers("драмбуи"): "Drambuie",
    _norm_keep_numbers("drambuie"): "Drambuie",

    _norm_keep_numbers("рейка"): "Reyka Vodka",
    _norm_keep_numbers("reyka"): "Reyka Vodka",

    _norm_keep_numbers("милагро"): "Milagro Silver",
    _norm_keep_numbers("milagro"): "Milagro Silver",

    _norm_keep_numbers("аэрстоун"): "Aerstone 10 Year Old Sea Cask",
    _norm_keep_numbers("aerstone"): "Aerstone 10 Year Old Sea Cask",

    _norm_keep_numbers("сейлор джерри"): "Sailor Jerry Spiced Rum",
    _norm_keep_numbers("сейлор"): "Sailor Jerry Spiced Rum",
    _norm_keep_numbers("джерри"): "Sailor Jerry Spiced Rum",
    _norm_keep_numbers("sailor jerry"): "Sailor Jerry Spiced Rum",
}

def _build_indexes() -> None:
    NAME_INDEX.clear(); ALIASES.clear(); ALIASES_NUM.clear(); ALL_CANON.clear()
    for entry in RAW:
        brand = (entry.get("brand") or "").strip()
        if not brand:
            continue
        key = _norm(brand)
        NAME_INDEX[key] = entry
        ALL_CANON.append(brand)

        # алиасы с цифрами (сначала)
        for alias in entry.get("aliases", []) or []:
            akey_num = _norm_keep_numbers(alias)
            if akey_num and akey_num not in ALIASES_NUM:
                ALIASES_NUM[akey_num] = brand

        # алиасы без цифр (вторым слоем)
        for alias in entry.get("aliases", []) or []:
            akey = _norm(alias)
            if akey and akey not in NAME_INDEX and akey not in ALIASES:
                ALIASES[akey] = brand

    # Добавим корневые алиасы, если такие бренды действительно есть
    for k, canon in list(ROOT_ALIASES.items()):
        if _norm(canon) in NAME_INDEX:
            ALIASES_NUM.setdefault(k, canon)

_build_indexes()

# ---------- помощники ----------
def _build_caption(entry: Dict[str, Any]) -> str:
    brand   = entry.get("brand", "")
    cat     = entry.get("category", "")
    country = entry.get("country", "")
    abv     = entry.get("abv", "")
    notes   = entry.get("tasting_notes", "")
    facts   = entry.get("production_facts", "")
    sell    = entry.get("sales_script", "")

    head = f"<b>{brand}</b>"
    meta = " · ".join([x for x in [cat, country, abv] if x])
    if meta: head += f"\n<i>{meta}</i>"

    parts = [head]
    if notes: parts.append(notes)
    if facts: parts.append(facts)
    if sell:  parts.append(f"<b>Как продавать:</b> {sell}")

    caption = "\n".join(parts)
    caption = re.sub(r"\n{3,}", "\n\n", caption).strip()
    if len(caption) > 1000:
        caption = caption[:997] + "…"
    return caption

def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

# ---------- ПУБЛИЧНОЕ API ----------
def exact_lookup(text: str) -> Optional[str]:
    """Ищем в 4 шага: NAME_INDEX -> ALIASES_NUM -> ROOT_ALIASES -> ALIASES."""
    key_num = _norm_keep_numbers(text)
    if key_num in NAME_INDEX:
        return NAME_INDEX[key_num].get("brand")
    if key_num in ALIASES_NUM:
        return ALIASES_NUM[key_num]
    if key_num in ROOT_ALIASES:
        return ROOT_ALIASES[key_num]

    key = _norm(text)
    if key in NAME_INDEX:
        return NAME_INDEX[key].get("brand")
    if key in ALIASES:
        return ALIASES[key]
    return None

def get_brand(name: str) -> Optional[Dict[str, Any]]:
    canon = exact_lookup(name) or name
    entry = NAME_INDEX.get(_norm(canon))
    if not entry:
        return None
    return {
        "name": entry.get("brand", canon),
        "caption": _build_caption(entry),
        "photo_file_id": entry.get("photo_file_id"),  # может быть None
        "image_url": entry.get("image_url"),          # опционально, если добавишь
        "category": entry.get("category", "")
    }

def by_category(cat_query: str, limit: int = 50) -> List[str]:
    q = _norm(cat_query)
    out: List[str] = []
    for entry in NAME_INDEX.values():
        cat = _norm(entry.get("category", ""))
        if q and q in cat:
            b = entry.get("brand")
            if b:
                out.append(b)
                if len(out) >= limit:
                    break
    return sorted(set(out))

def fuzzy_suggest(text: str, limit: int = 10) -> List[Tuple[str, float]]:
    t = (text or "").strip()
    if not t:
        return []
    t_norm_num = _norm_keep_numbers(t)
    t_norm = _norm(t)

    candidates = set(ALL_CANON)
    for _, canon in ALIASES.items():
        candidates.add(canon)
    for _, canon in ALIASES_NUM.items():
        candidates.add(canon)

    # быстрые подстрочные попадания (и с цифрами, и без)
    hits = [(c, 1.0) for c in candidates if (t_norm and t_norm in _norm(c)) or (t_norm_num and t_norm_num in _norm_keep_numbers(c))]

    # похожесть
    scored: List[Tuple[str, float]] = []
    for c in candidates:
        s1 = _similar(t_norm_num, _norm_keep_numbers(c))
        s2 = _similar(t_norm, _norm(c))
        s = max(s1, s2)
        if s >= 0.6:
            scored.append((c, s))

    by_name: Dict[str, float] = {n: s for n, s in scored}
    for n, s in hits:
        by_name[n] = max(by_name.get(n, 0.0), s)

    return sorted(by_name.items(), key=lambda x: x[1], reverse=True)[:limit]

# ---------- РУССКИЕ СИНОНИМЫ (если где-то импорт русскими именами) ----------
по_категории = by_category
точный_поиск = exact_lookup
нечеткий_подсказка = fuzzy_suggest
получить_бренд = get_brand
# --- Автосохранение URL картинки в локальную базу ---
def set_image_url_for_brand(name: str, url: str) -> bool:
    """
    Если у бренда нет photo_file_id — сохраняем image_url в data/catalog.json.
    Обновляем память и индексы, чтобы сработало без перезапуска.
    Возвращает True, если записали на диск.
    """
    try:
        from pathlib import Path
        import json

        name_clean = (name or "").strip()
        if not name_clean or not url:
            return False

        path = Path("data/catalog.json")
        # читаем существующее содержимое (список объектов)
        data = []
        if path.exists():
            try:
                raw = path.read_text(encoding="utf-8")
                loaded = json.loads(raw)
                data = loaded if isinstance(loaded, list) else []
            except Exception:
                data = []

        # ищем запись по точному совпадению brand
        idx = -1
        for i, it in enumerate(data):
            if (it.get("brand") or "").strip().lower() == name_clean.lower():
                idx = i
                break

        if idx >= 0:
            item = dict(data[idx])
            # если уже есть file_id — ничего не трогаем
            if item.get("photo_file_id"):
                pass
            else:
                # не затираем существующий image_url, если он уже есть
                item.setdefault("image_url", url)
                data[idx] = item
        else:
            # новой записи достаточно brand + image_url
            data.append({"brand": name_clean, "image_url": url})

        # пишем на диск (красиво, UTF-8)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        # --- Обновляем память и индексы, чтобы сразу заработало ---
        try:
            # RAW и индексируются в этом модуле
            global RAW
            updated = False
            for it in RAW:
                if (it.get("brand") or "").strip().lower() == name_clean.lower():
                    if not it.get("photo_file_id"):
                        it.setdefault("image_url", url)
                    updated = True
                    break
            if not updated:
                RAW.append({"brand": name_clean, "image_url": url})

            # пересобираем индексы
            _build_indexes()
        except Exception:
            pass

        return True
    except Exception as e:
        print("[brands] set_image_url_for_brand error:", e)
        return False


# --- helper for vision keyboard (compat) ---
try:
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    def _kb_find(query: str, limit: int = 8):
        try:
            pairs = fuzzy_suggest(query, limit=limit)
            names = [p[0] if isinstance(p, tuple) else str(p) for p in pairs][:limit]
            if not names:
                return None
            rows = [[InlineKeyboardButton(text=name, callback_data=f"brand:{name}")] for name in names]
            return InlineKeyboardMarkup(inline_keyboard=rows)
        except Exception:
            return None
except Exception:
    def _kb_find(query: str, limit: int = 8):
        return None


def suggest_candidates(query: str, top_n: int = 10):
    q = _norm(query)
    if not q:
        return []
    q_cf = q.casefold()
    q_tr = translit_ru_to_en(q_cf)
    # alias expansion to get seed
    seeds = [q]
    if q_cf in ALIASES:
        seeds.append(ALIASES[q_cf])
    # collect candidates by substring in normal or transliterated space
    idx = _catalog_index()
    scores = {}
    for disp, cf, tr in idx:
        for s in [q_cf, q_tr] + [x.casefold() for x in seeds]:
            if not s:
                continue
            # simple scoring
            score = 0
            if s in cf or s in tr:
                score += 3 + len(s)/max(1,len(cf))
            # token overlap
            cf_tokens = set(cf.split())
            s_tokens = set(s.split())
            inter = len(cf_tokens & s_tokens)
            if inter:
                score += 2*inter
            # prefix boost
            if cf.startswith(s) or tr.startswith(s):
                score += 1.5
            if score>0:
                scores[disp] = max(scores.get(disp,0), score)
    # sort by score desc then name
    ordered = sorted(scores.items(), key=lambda x:(-x[1], x[0]))
    return [name for name,_ in ordered][:top_n]


def brand_card(name: str):
    return None


# --- Cyrillic → Latin rough transliteration for search ---
_RU2EN = {
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"y",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f",
    "х":"h","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
}
def translit_ru_to_en(text: str) -> str:
    t = (text or "").lower()
    return "".join(_RU2EN.get(ch, ch) for ch in t)

def _norm(s: str) -> str:
    return (s or "").strip()

def _catalog_index():
    # build cf-name -> record map + searchable strings
    data = _load_raw() if " _load_raw" in globals() else (CATALOG if 'CATALOG' in globals() else [])
    idx = []
    for rec in data:
        nm = _norm(rec.get("brand") or rec.get("name"))
        if not nm: 
            continue
        nm_lc = nm.casefold()
        idx.append((nm, nm_lc, translit_ru_to_en(nm_lc)))
    return idx
