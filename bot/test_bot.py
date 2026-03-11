"""Тестовый скрипт для проверки работы бота без БД"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Токены из .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Я бот для получения информации о погоде и новостях.\n\n"
        f"Доступные команды:\n"
        f"/start - Это сообщение\n"
        f"/test_weather - Тест API погоды\n"
        f"/test_news - Тест API новостей\n"
        f"/help - Помощь"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📋 Доступные команды:\n\n"
        "/start - Начать работу\n"
        "/test_weather - Проверить API погоды\n"
        "/test_news - Проверить API новостей\n"
        "/help - Эта справка"
    )


@dp.message(Command("test_weather"))
async def cmd_test_weather(message: Message):
    """Тест API погоды"""
    import aiohttp
    
    await message.answer("🔄 Проверяю API погоды...")
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": "Moscow",
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "ru"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = round(data["main"]["temp"])
                    description = data["weather"][0]["description"]
                    
                    await message.answer(
                        f"✅ API погоды работает!\n\n"
                        f"🌤 Погода в Москве:\n"
                        f"🌡 Температура: {temp}°C\n"
                        f"📝 {description.capitalize()}"
                    )
                else:
                    await message.answer(f"❌ Ошибка API: {response.status}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("test_news"))
async def cmd_test_news(message: Message):
    """Тест API новостей"""
    import aiohttp
    
    await message.answer("🔄 Проверяю API новостей...")
    
    try:
        url = "https://api.currentsapi.services/v1/latest-news"
        params = {
            "apiKey": NEWS_API_KEY,
            "language": "ru",
            "page_size": 3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    news = data.get("news", [])
                    
                    if news:
                        text = "✅ API новостей работает!\n\n📰 Топ новости:\n\n"
                        for i, article in enumerate(news[:3], 1):
                            text += f"{i}. {article.get('title', 'Без заголовка')}\n\n"
                        
                        await message.answer(text)
                    else:
                        await message.answer("❌ Новости не найдены")
                else:
                    await message.answer(f"❌ Ошибка API: {response.status}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


async def main():
    """Главная функция"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден в .env файле!")
        return
    
    if not WEATHER_API_KEY:
        logger.warning("⚠️  WEATHER_API_KEY не найден в .env файле!")
    
    if not NEWS_API_KEY:
        logger.warning("⚠️  NEWS_API_KEY не найден в .env файле!")
    
    logger.info("🚀 Бот запускается...")
    logger.info(f"Bot token: {BOT_TOKEN[:10]}...")
    
    try:
        # Удаление вебхука
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Бот успешно запущен!")
        logger.info("📝 Найдите бота в Telegram и отправьте /start")
        
        # Запуск polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
