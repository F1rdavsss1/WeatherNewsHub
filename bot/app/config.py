"""Конфигурация бота"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Bot
    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "telegram_bot"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # API Keys
    WEATHER_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    
    # Cache TTL (seconds)
    WEATHER_CACHE_TTL: int = 300
    NEWS_CACHE_TTL: int = 1800
    THROTTLE_TIME: int = 1
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    @property
    def database_url(self) -> str:
        """Формирование URL для подключения к БД"""
        # Используем SQLite по умолчанию (согласно ТЗ)
        return "sqlite+aiosqlite:///bot.db"
        # Для PostgreSQL раскомментируйте:
        # return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """Формирование URL для подключения к Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def admin_list(self) -> List[int]:
        """Список ID администраторов"""
        if not self.ADMIN_IDS:
            return []
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS.split(",")]


settings = Settings()
