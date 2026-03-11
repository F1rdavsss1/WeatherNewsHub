"""Упрощенная версия бота с SQLite вместо PostgreSQL"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.handlers import setup_routers
from app.middlewares.db import DatabaseMiddleware
from app.models.base import Base

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def create_db_tables(engine):
    """Создание таблиц в БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы БД созданы")


async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота (упрощенная версия с SQLite)...")
    
    # Инициализация бота
    bot = Bot(token=settings.BOT_TOKEN)
    
    # FSM хранилище в памяти (без Redis)
    storage = MemoryStorage()
    
    # Диспетчер
    dp = Dispatcher(storage=storage)
    
    # Подключение к SQLite
    engine = create_async_engine(
        "sqlite+aiosqlite:///bot.db",
        echo=False
    )
    
    # Создание таблиц
    await create_db_tables(engine)
    
    # Session maker
    session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False
    )
    
    # Регистрация middleware
    dp.update.middleware(DatabaseMiddleware(session_maker))
    
    # Создаем простой Redis-заглушку для кэширования в памяти
    class SimpleCache:
        def __init__(self):
            self.cache = {}
        
        async def get(self, key):
            return self.cache.get(key)
        
        async def setex(self, key, ttl, value):
            self.cache[key] = value
        
        async def delete(self, key):
            self.cache.pop(key, None)
        
        async def close(self):
            pass
    
    redis_cache = SimpleCache()
    
    # Добавление кэша в контекст
    dp.workflow_data.update({"redis": redis_cache})
    
    # Регистрация роутеров
    dp.include_router(setup_routers())
    
    try:
        # Удаление вебхука (если был установлен)
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Бот успешно запущен (SQLite + Memory Storage)")
        logger.info("📝 Найдите бота в Telegram: @WeatherNewsHubot")
        logger.info("💡 Используется SQLite вместо PostgreSQL")
        logger.info("💡 Кэш в памяти вместо Redis")
        
        # Запуск polling
        await dp.start_polling(bot, redis=redis_cache)
    finally:
        # Закрытие соединений
        await redis_cache.close()
        await engine.dispose()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
