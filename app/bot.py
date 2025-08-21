from aiogram import Dispatcher
from app.middlewares.errors import ErrorsLoggingMiddleware
from app.routers import main as main_router
from app.routers import brands as brands_router
from app.routers import ai_helper as ai_helper_router
from app.routers import vision as vision_router
from app.routers import posm_simple as posm_simple_router

dp = Dispatcher()
dp.message.middleware(ErrorsLoggingMiddleware())

def include_once(dp, r):
    if getattr(r, "parent_router", None) is None:
        dp.include_router(r)

include_once(dp, main_router.router)
include_once(dp, brands_router.router)
include_once(dp, vision_router.router)
include_once(dp, posm_simple_router.router)
include_once(dp, ai_helper_router.router)
