"""Инициализация базы данных и заполнение начальными данными"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.base import Base
from app.models.user import NewsCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Категории новостей согласно ТЗ
NEWS_CATEGORIES_DATA = [
    ("general", "Главные новости", "General"),
    ("technology", "Технологии", "Technology"),
    ("science", "Наука", "Science"),
    ("sports", "Спорт", "Sports"),
    ("business", "Бизнес", "Business"),
    ("health", "Здоровье", "Health"),
    ("entertainment", "Развлечения", "Entertainment"),
]


async def init_database():
    """Создание таблиц и заполнение начальными данными"""
    logger.info("Инициализация базы данных...")
    
    # Создание движка
    engine = create_async_engine(
        settings.database_url,
        echo=True
    )
    
    # Создание всех таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляем старые таблицы
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Таблицы созданы")
    
    # Создание сессии
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    async with session_maker() as session:
        # Проверка существующих категорий
        stmt = select(NewsCategory)
        result = await session.execute(stmt)
        existing_categories = result.scalars().all()
        
        if existing_categories:
            logger.info(f"Категории новостей уже существуют ({len(existing_categories)} шт.)")
        else:
            # Добавление категорий новостей
            logger.info("Добавление категорий новостей...")
            
            for code, name_ru, name_en in NEWS_CATEGORIES_DATA:
                category = NewsCategory(
                    category_code=code,
                    category_name_ru=name_ru,
                    category_name_en=name_en
                )
                session.add(category)
            
            await session.commit()
            logger.info(f"✅ Добавлено {len(NEWS_CATEGORIES_DATA)} категорий новостей")
    
    await engine.dispose()
    logger.info("✅ База данных инициализирована")


if __name__ == "__main__":
    asyncio.run(init_database())
