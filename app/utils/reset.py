def reset_user(uid: int):
    for mod, attr in [
        ("app.routers.ai_helper", "AI_USERS"),
        ("app.routers.brands", "CATALOG_USERS"),
        ("app.routers.vision", "VISION_USERS"),
        ("app.routers.posm_simple", "POSM_USERS"),
    ]:
        try:
            m = __import__(mod, fromlist=[attr])
            getattr(m, attr).discard(uid)
        except Exception:
            pass
