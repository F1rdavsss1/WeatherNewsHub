"""Обработчики команд новостей"""
import logging
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import redis.asyncio as aioredis

from app.utils.news_api import news_api, NewsAPI
from app.keyboards.inline import get_news_categories_keyboard
from app.config import settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("news"))
@router.message(F.text == "📰 Новости")
async def cmd_news(message: Message, redis: aioredis.Redis):
    """Обработчик команды /news"""
    args = message.text.split(maxsplit=1)
    
    # Определение категории
    if len(args) > 1 and message.text.startswith("/news"):
        category = args[1].lower()
        if category not in NewsAPI.CATEGORIES:
            await message.answer(
                f"❌ Неизвестная категория. Доступные категории:\n" +
                "\n".join([f"• {cat}" for cat in NewsAPI.CATEGORIES.keys()])
            )
            return
    else:
        # Показать клавиатуру с категориями
        await message.answer(
            "Выберите категорию новостей:",
            reply_markup=get_news_categories_keyboard()
        )
        return
    
    await send_news(message, category, redis)


@router.message(Command("categories"))
async def cmd_categories(message: Message):
    """Список категорий новостей"""
    categories_text = "📰 Доступные категории новостей:\n\n"
    
    for code, name in NewsAPI.CATEGORIES.items():
        categories_text += f"• {name} - /news {code}\n"
    
    categories_text += "\nИспользование: /news <категория>\nПример: /news technology"
    
    await message.answer(categories_text)


async def send_news(message: Message, category: str, redis: aioredis.Redis):
    """Отправка новостей по категории"""
    # Проверка кэша
    cache_key = f"news:{category}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        news = json.loads(cached_data)
        logger.info(f"Новости категории {category} получены из кэша")
    else:
        news = await news_api.get_top_headlines(category=category, page_size=5)
        
        if not news:
            await message.answer("❌ Не удалось получить новости. Попробуйте позже.")
            return
        
        await redis.setex(
            cache_key,
            settings.NEWS_CACHE_TTL,
            json.dumps(news, ensure_ascii=False)
        )
    
    # Формирование ответа
    category_name = NewsAPI.get_category_name(category)
    news_text = f"📰 Топ новости ({category_name}):\n\n"
    
    for i, article in enumerate(news, 1):
        news_text += (
            f"{i}. {article['title']}\n"
            f"📌 {article['source']}\n"
            f"🔗 {article['url']}\n\n"
        )
    
    await message.answer(news_text, disable_web_page_preview=True)
