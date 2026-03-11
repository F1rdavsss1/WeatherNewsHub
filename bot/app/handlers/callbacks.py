"""Обработчики callback-запросов от инлайн-кнопок"""
import logging
import json
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.models.user import User, Favorite
from app.utils.weather_api import weather_api
from app.utils.news_api import news_api, NewsAPI
from app.keyboards.inline import get_weather_actions_keyboard
from app.config import settings
from app.handlers.news import send_news

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("news_"))
async def process_news_category(callback: CallbackQuery, redis: aioredis.Redis):
    """Обработка выбора категории новостей"""
    category = callback.data.split("_", 1)[1]
    
    await callback.answer()
    await send_news(callback.message, category, redis)


@router.callback_query(F.data.startswith("forecast_"))
async def process_forecast(callback: CallbackQuery, redis: aioredis.Redis):
    """Обработка запроса прогноза"""
    parts = callback.data.split("_")
    city = parts[1]
    days = int(parts[2])
    
    await callback.answer("Получаю прогноз...")
    
    # Проверка кэша
    cache_key = f"forecast:{city.lower()}:{days}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        forecast = json.loads(cached_data)
    else:
        forecast = await weather_api.get_forecast(city, days)
        
        if not forecast:
            await callback.message.answer(f"❌ Не удалось получить прогноз для города '{city}'.")
            return
        
        await redis.setex(
            cache_key,
            settings.WEATHER_CACHE_TTL,
            json.dumps(forecast, ensure_ascii=False)
        )
    
    # Формирование ответа
    forecast_text = f"📅 Прогноз погоды для {forecast['city']}, {forecast['country']}:\n\n"
    
    for day in forecast['forecast']:
        forecast_text += (
            f"📆 {day['date']}\n"
            f"🌡 {day['temp_min']}°C ... {day['temp_max']}°C\n"
            f"📝 {day['description']}\n\n"
        )
    
    await callback.message.answer(forecast_text)


@router.callback_query(F.data.startswith("add_favorite_"))
async def process_add_favorite(callback: CallbackQuery, session: AsyncSession):
    """Добавление города в избранное"""
    city = callback.data.split("_", 2)[2]
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == callback.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Ошибка. Используйте /start", show_alert=True)
        return
    
    # Проверка существования
    stmt = select(Favorite).where(
        Favorite.user_id == user.id,
        Favorite.city_name == city
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        await callback.answer("Этот город уже в избранном!", show_alert=True)
        return
    
    # Добавление в избранное
    favorite = Favorite(user_id=user.id, city_name=city)
    session.add(favorite)
    await session.commit()
    
    await callback.answer(f"✅ {city} добавлен в избранное!")


@router.callback_query(F.data.startswith("remove_favorite_"))
async def process_remove_favorite(callback: CallbackQuery, session: AsyncSession):
    """Удаление города из избранного"""
    city = callback.data.split("_", 2)[2]
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == callback.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    # Удаление из избранного
    stmt = select(Favorite).where(
        Favorite.user_id == user.id,
        Favorite.city_name == city
    )
    result = await session.execute(stmt)
    favorite = result.scalar_one_or_none()
    
    if favorite:
        await session.delete(favorite)
        await session.commit()
        await callback.answer(f"✅ {city} удален из избранного")
        
        # Обновление списка
        from app.handlers.settings import cmd_favorites
        await cmd_favorites(callback.message, session)
    else:
        await callback.answer("❌ Город не найден в избранном", show_alert=True)


@router.callback_query(F.data.startswith("refresh_weather_"))
async def process_refresh_weather(callback: CallbackQuery, redis: aioredis.Redis):
    """Обновление погоды"""
    city = callback.data.split("_", 2)[2]
    
    await callback.answer("Обновляю данные...")
    
    # Удаление из кэша для принудительного обновления
    cache_key = f"weather:{city.lower()}"
    await redis.delete(cache_key)
    
    # Получение свежих данных
    weather = await weather_api.get_current_weather(city)
    
    if not weather:
        await callback.message.answer(f"❌ Не удалось обновить погоду для '{city}'.")
        return
    
    # Сохранение в кэш
    await redis.setex(
        cache_key,
        settings.WEATHER_CACHE_TTL,
        json.dumps(weather, ensure_ascii=False)
    )
    
    # Формирование ответа
    weather_text = (
        f"🌤 Погода в {weather['city']}, {weather['country']}\n\n"
        f"🌡 Температура: {weather['temp']}°C\n"
        f"🤔 Ощущается как: {weather['feels_like']}°C\n"
        f"📝 {weather['description']}\n"
        f"💨 Ветер: {weather['wind_speed']} м/с\n"
        f"💧 Влажность: {weather['humidity']}%\n"
        f"🔽 Давление: {weather['pressure']} гПа"
    )
    
    await callback.message.edit_text(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )


@router.callback_query(F.data.startswith("show_forecast_"))
async def process_show_forecast(callback: CallbackQuery):
    """Показать клавиатуру выбора прогноза"""
    from app.keyboards.inline import get_forecast_keyboard
    
    city = callback.data.split("_", 2)[2]
    
    await callback.message.answer(
        f"Выберите период прогноза для {city}:",
        reply_markup=get_forecast_keyboard(city)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("weather_favorite_"))
async def process_weather_favorite(callback: CallbackQuery, redis: aioredis.Redis):
    """Показать погоду для избранного города"""
    city = callback.data.split("_", 2)[2]
    
    await callback.answer("Получаю погоду...")
    
    # Проверка кэша
    cache_key = f"weather:{city.lower()}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        weather = json.loads(cached_data)
    else:
        weather = await weather_api.get_current_weather(city)
        
        if not weather:
            await callback.message.answer(f"❌ Не удалось получить погоду для '{city}'.")
            return
        
        await redis.setex(
            cache_key,
            settings.WEATHER_CACHE_TTL,
            json.dumps(weather, ensure_ascii=False)
        )
    
    weather_text = (
        f"🌤 Погода в {weather['city']}, {weather['country']}\n\n"
        f"🌡 Температура: {weather['temp']}°C\n"
        f"🤔 Ощущается как: {weather['feels_like']}°C\n"
        f"📝 {weather['description']}\n"
        f"💨 Ветер: {weather['wind_speed']} м/с\n"
        f"💧 Влажность: {weather['humidity']}%\n"
        f"🔽 Давление: {weather['pressure']} гПа"
    )
    
    await callback.message.answer(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )
