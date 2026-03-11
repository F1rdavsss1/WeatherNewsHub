"""Главный файл запуска бота"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import redis.asyncio as aioredis

from app.config import settings
from app.handlers import setup_routers
from app.middlewares.db import DatabaseMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.utils.scheduler import NotificationScheduler
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
    logger.info("Запуск бота...")
    
    # Инициализация бота
    bot = Bot(token=settings.BOT_TOKEN)
    
    # Подключение к Redis
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    
    # FSM хранилище в Redis
    storage = RedisStorage(redis=redis_client)
    
    # Диспетчер
    dp = Dispatcher(storage=storage)
    
    # Подключение к БД
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True
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
    dp.message.middleware(ThrottlingMiddleware(redis_client))
    
    # Добавление Redis в контекст
    dp.workflow_data.update({"redis": redis_client})
    
    # Регистрация роутеров
    dp.include_router(setup_routers())
    
    # Запуск планировщика уведомлений
    scheduler = NotificationScheduler(bot, session_maker)
    scheduler.start()
    
    try:
        # Удаление вебхука (если был установлен)
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот успешно запущен")
        
        # Запуск polling
        await dp.start_polling(bot, redis=redis_client)
    finally:
        # Остановка планировщика
        scheduler.stop()
        
        # Закрытие соединений
        await redis_client.close()
        await engine.dispose()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
