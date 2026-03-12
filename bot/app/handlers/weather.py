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
async def cmd_weather(message: Message, session: AsyncSession, state: FSMContext):
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
    
    # Запрос к API (без кэша)
    weather = await weather_api.get_current_weather(city)
    
    if not weather:
        await message.answer(f"❌ Город '{city}' не найден. Проверьте правильность написания.")
        return
    
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
async def process_weather_city(message: Message, state: FSMContext):
    """Обработка ввода города для погоды"""
    city = message.text.strip()
    
    if city == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    # Запрос к API (без кэша)
    weather = await weather_api.get_current_weather(city)
    
    if not weather:
        await message.answer(
            f"❌ Город '{city}' не найден. Попробуйте еще раз или отправьте '❌ Отмена'."
        )
        return
    
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
async def cmd_forecast(message: Message):
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
    
    # Запрос к API (без кэша)
    forecast = await weather_api.get_forecast(city, days)
    
    if not forecast:
        await message.answer(f"❌ Не удалось получить прогноз для города '{city}'.")
        return
    
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
async def cmd_mycity(message: Message, session: AsyncSession):
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
    
    # Запрос к API (без кэша)
    weather = await weather_api.get_current_weather(city)
    
    if not weather:
        await message.answer(f"❌ Не удалось получить погоду для '{city}'.")
        return
    
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
