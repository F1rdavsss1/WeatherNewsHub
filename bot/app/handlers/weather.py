"""Обработчики команд погоды"""
import logging
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.models.user import User
from app.states.user_states import WeatherState
from app.utils.weather_api import weather_api
from app.keyboards.inline import get_weather_actions_keyboard, get_forecast_keyboard
from app.config import settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("weather"))
@router.message(F.text == "🌤 Погода")
async def cmd_weather(message: Message, session: AsyncSession, state: FSMContext, redis: aioredis.Redis):
    """Обработчик команды /weather"""
    # Парсинг аргументов
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2 and message.text != "🌤 Погода":
        # Проверка города по умолчанию
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user and user.default_city:
            city = user.default_city
        else:
            await message.answer(
                "Укажите город:\n"
                "/weather <город>\n\n"
                "Или установите город по умолчанию: /setcity <город>"
            )
            return
    elif message.text == "🌤 Погода":
        # Проверка города по умолчанию
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user and user.default_city:
            city = user.default_city
        else:
            await message.answer("Введите название города:")
            await state.set_state(WeatherState.waiting_for_city)
            return
    else:
        city = args[1]
    
    # Проверка кэша
    cache_key = f"weather:{city.lower()}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        weather = json.loads(cached_data)
        logger.info(f"Погода для {city} получена из кэша")
    else:
        # Запрос к API
        weather = await weather_api.get_current_weather(city)
        
        if not weather:
            await message.answer(f"❌ Город '{city}' не найден. Проверьте правильность написания.")
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
    
    await message.answer(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )


@router.message(WeatherState.waiting_for_city)
async def process_weather_city(message: Message, state: FSMContext, redis: aioredis.Redis):
    """Обработка ввода города для погоды"""
    city = message.text.strip()
    
    if city == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    # Проверка кэша
    cache_key = f"weather:{city.lower()}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        weather = json.loads(cached_data)
    else:
        weather = await weather_api.get_current_weather(city)
        
        if not weather:
            await message.answer(
                f"❌ Город '{city}' не найден. Попробуйте еще раз или отправьте '❌ Отмена'."
            )
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
    
    await message.answer(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )
    await state.clear()


@router.message(Command("forecast"))
async def cmd_forecast(message: Message, redis: aioredis.Redis):
    """Обработчик команды /forecast"""
    args = message.text.split()
    
    if len(args) < 2:
        await message.answer("Использование: /forecast <город> [дни]\nПример: /forecast Москва 5")
        return
    
    city = args[1]
    days = int(args[2]) if len(args) > 2 else 5
    
    if days < 1 or days > 7:
        await message.answer("❌ Количество дней должно быть от 1 до 7.")
        return
    
    # Проверка кэша
    cache_key = f"forecast:{city.lower()}:{days}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        forecast = json.loads(cached_data)
    else:
        forecast = await weather_api.get_forecast(city, days)
        
        if not forecast:
            await message.answer(f"❌ Не удалось получить прогноз для города '{city}'.")
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
    
    await message.answer(forecast_text)


@router.message(Command("mycity"))
async def cmd_mycity(message: Message, session: AsyncSession, redis: aioredis.Redis):
    """Погода в сохраненном городе"""
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.default_city:
        await message.answer(
            "У вас не установлен город по умолчанию.\n"
            "Используйте: /setcity <город>"
        )
        return
    
    city = user.default_city
    
    # Проверка кэша
    cache_key = f"weather:{city.lower()}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        weather = json.loads(cached_data)
    else:
        weather = await weather_api.get_current_weather(city)
        
        if not weather:
            await message.answer(f"❌ Не удалось получить погоду для '{city}'.")
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
    
    await message.answer(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )
