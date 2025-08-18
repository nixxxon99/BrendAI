from app.routers import posm_simple as posm_simple_router
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

from app.settings import settings
from app.middlewares.error_logging import ErrorsLoggingMiddleware
from app.routers import brands as brands_router
from app.routers import vision as vision_router
from app.routers import catalog as catalog_router
from app.routers import posm_simple as posm_router
from app.routers import main as main_router
from app.routers import ai_helper as ai_helper_router  # <-- новый роутер
from app.routers import admin_tools as admin_tools_router
from app.routers import posm as posm_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")

bot = Bot(settings.API_TOKEN, parse_mode="HTML")
dp = Dispatcher()
dp.message.middleware(ErrorsLoggingMiddleware())

# Routers
dp.include_router(ai_helper_router.router)  # <-- подключаем
# photo recognition

# Router includes (order matters)
dp.include_router(main_router.router)
dp.include_router(brands_router.router)
dp.include_router(vision_router.router)
dp.include_router(posm_simple_router.router)
dp.include_router(admin_tools_router.router)
dp.include_router(ai_helper_router.router)
