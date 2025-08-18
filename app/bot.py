import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

from app.settings import settings
from app.middlewares.error_logging import ErrorsLoggingMiddleware
from app.routers import brands as brands_router
from app.routers import vision as vision_router
from app.routers import catalog as catalog_router
from app.routers import posm_simple as posm_simple_router
from app.routers import main as main_router
from app.routers import ai_helper as ai_helper_router  # <-- новый роутер
from app.routers import admin_tools as admin_tools_router
from app.routers import posm as posm_full_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")

bot = Bot(settings.API_TOKEN, parse_mode="HTML")
dp = Dispatcher()
dp.message.middleware(ErrorsLoggingMiddleware())

def include_once(dp, r):
    if getattr(r, 'parent_router', None) is None:
        dp.include_router(r)

# Routers
include_once(dp, main_router.router)
include_once(dp, ai_helper_router.router)  # <-- подключаем
include_once(dp, brands_router.router)


# photo recognition
include_once(dp, vision_router.router)
include_once(dp, catalog_router.router)
include_once(dp, posm_full_router.router)

include_once(dp, posm_simple_router.router)
