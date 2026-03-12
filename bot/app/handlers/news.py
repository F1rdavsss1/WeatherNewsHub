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
async def cmd_news(message: Message):
    """Обработчик команды /news - показывает категории или новости"""
    args = message.text.split(maxsplit=1)
    
    # Если указана категория
    if len(args) > 1 and message.text.startswith("/news"):
        category = args[1].lower()
        if category not in NewsAPI.CATEGORIES:
            await message.answer(
                f"❌ Неизвестная категория '{category}'.\n\n"
                f"📰 Доступные категории:\n" +
                "\n".join([f"• {name} - /news {code}" for code, name in NewsAPI.CATEGORIES.items()])
            )
            return
        await send_news(message, category)
    else:
        # Показать клавиатуру с категориями
        await message.answer(
            "📰 Выберите категорию новостей:\n\n" +
            "\n".join([f"• {name} - /news {code}" for code, name in NewsAPI.CATEGORIES.items()]),
            reply_markup=get_news_categories_keyboard()
        )
        return


@router.message(Command("categories"))
async def cmd_categories(message: Message):
    """Список категорий новостей"""
    categories_text = "📰 Доступные категории новостей:\n\n"
    
    for code, name in NewsAPI.CATEGORIES.items():
        categories_text += f"• {name} - /news {code}\n"
    
    categories_text += "\nИспользование: /news <категория>\nПример: /news technology"
    
    await message.answer(categories_text)


async def send_news(message: Message, category: str):
    """Отправка новостей по категории без картинок"""
    # Запрос к API
    news = await news_api.get_top_headlines(category=category, page_size=5)
    
    if not news:
        await message.answer("❌ Не удалось получить новости. Попробуйте позже.")
        return
    
    # Формирование ответа без картинок
    category_name = NewsAPI.get_category_name(category)
    news_text = f"📰 Топ-5 новостей ({category_name}):\n\n"
    
    for i, article in enumerate(news, 1):
        news_text += (
            f"{i}. {article['title']}\n"
            f"📌 {article['source']}\n"
            f"🔗 {article['url']}\n\n"
        )
    
    await message.answer(news_text, disable_web_page_preview=True)
