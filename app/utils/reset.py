# app/utils/reset.py
def reset_user(uid: int):
    "Best-effort: выгружаем пользователя из всех 'режимных' множеств."
    try:
        from app.routers.ai_helper import AI_USERS
        AI_USERS.discard(uid)
    except Exception:
        pass
    try:
        from app.routers.vision import VISION_USERS
        VISION_USERS.discard(uid)
    except Exception:
        pass
    try:
        from app.routers.brands import CATALOG_USERS
        CATALOG_USERS.discard(uid)
    except Exception:
        pass
    try:
        from app.routers.posm_simple import POSM_USERS
        POSM_USERS.discard(uid)
    except Exception:
        pass
