# app/settings.py — совместимый Settings (Pydantic v2)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    # Telegram token: принимаем из нескольких имён
    API_TOKEN: str = Field(validation_alias=AliasChoices("API_TOKEN", "BOT_TOKEN", "TELEGRAM_BOT_TOKEN"))

    # Timezone: TIMEZONE или TZ
    TIMEZONE: str = Field(default="Asia/Almaty", validation_alias=AliasChoices("TIMEZONE", "TZ"))

    # Webhook URL/secret
    webhook_url: str | None = Field(default=None, validation_alias=AliasChoices("WEBHOOK_URL"))
    webhook_secret: str = Field(default="secret", validation_alias=AliasChoices("WEBHOOK_SECRET"))

    # Redis URL (не обязательно)
    REDIS_URL: str | None = Field(default=None, validation_alias=AliasChoices("REDIS_URL", "REDIS"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Совместимость со старым кодом ---
    @property
    def api_token(self) -> str:
        return self.API_TOKEN

    @property
    def tz(self) -> str:
        return self.TIMEZONE

    @property
    def redis_url(self) -> str:
        return self.REDIS_URL or ""

settings = Settings()
