# app/settings.py (patched)
from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    # Принимаем токен из нескольких имён переменных окружения
    API_TOKEN: str = Field(validation_alias=AliasChoices("API_TOKEN", "BOT_TOKEN", "TELEGRAM_BOT_TOKEN"))

    # Вебхук
    webhook_url: str | None = Field(default=None, validation_alias=AliasChoices("WEBHOOK_URL"))
    webhook_secret: str = Field(default="secret", validation_alias=AliasChoices("WEBHOOK_SECRET"))

    # Прочее
    TIMEZONE: str = "Asia/Almaty"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
