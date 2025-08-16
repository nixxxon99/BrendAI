from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    # Бот-токен: принимаем из нескольких имён переменных окружения
    API_TOKEN: str = Field(validation_alias=AliasChoices("API_TOKEN", "BOT_TOKEN", "TELEGRAM_BOT_TOKEN"))

    # Часовой пояс. Поддерживаем и TIMEZONE, и TZ. 
    TIMEZONE: str = Field(default="Asia/Almaty", validation_alias=AliasChoices("TIMEZONE", "TZ"))

    # Вебхуки
    webhook_url: str | None = Field(default=None, validation_alias=AliasChoices("WEBHOOK_URL"))
    webhook_secret: str = Field(default="secret", validation_alias=AliasChoices("WEBHOOK_SECRET"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # Совместимость: некоторые модули ожидают settings.tz
    @property
    def tz(self) -> str:
        return self.TIMEZONE

settings = Settings()
