"""Обработчики callback-запросов от инлайн-кнопок (упрощенная версия без Redis)"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, FavoriteCity
from app.utils.weather_api import weather_api
from app.utils.news_api import news_api, NewsAPI
from app.keyboards.inline import get_weather_actions_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("news_"))
async def process_news_category(callback: CallbackQuery):
    """Обработка выбора категории новостей без картинок"""
    category = callback.data.split("_", 1)[1]
    
    # Сразу отвечаем на callback чтобы убрать "часики"
    await callback.answer("Загружаю новости...")
    
    # Получение новостей
    news = await news_api.get_top_headlines(category=category, page_size=5)
    
    if not news:
        await callback.message.answer("❌ Не удалось получить новости.")
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
    
    # Удаляем клавиатуру и отправляем новости
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(news_text, disable_web_page_preview=True)


@router.callback_query(F.data.startswith("forecast_"))
async def process_forecast(callback: CallbackQuery):
    """Обработка запроса прогноза"""
    parts = callback.data.split("_")
    city = parts[1]
    days = int(parts[2])
    
    await callback.answer("Получаю прогноз...")
    
    forecast = await weather_api.get_forecast(city, days)
    
    if not forecast:
        await callback.message.answer(f"❌ Не удалось получить прогноз для города '{city}'.")
        return
    
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
    user_id = callback.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    # Проверка существования
    stmt = select(FavoriteCity).where(
        FavoriteCity.user_id == user.id,
        FavoriteCity.city_name == city
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        await callback.answer("⚠️ Город уже в избранном", show_alert=True)
        return
    
    # Добавление
    favorite = FavoriteCity(
        user_id=user.id,
        city_name=city
    )
    session.add(favorite)
    await session.commit()
    
    await callback.answer(f"✅ {city} добавлен в избранное!")


@router.callback_query(F.data.startswith("remove_favorite_"))
async def process_remove_favorite(callback: CallbackQuery, session: AsyncSession):
    """Удаление города из избранного"""
    city = callback.data.split("_", 2)[2]
    user_id = callback.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    # Поиск и удаление
    stmt = select(FavoriteCity).where(
        FavoriteCity.user_id == user.id,
        FavoriteCity.city_name == city
    )
    result = await session.execute(stmt)
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        await callback.answer("❌ Город не найден в избранном", show_alert=True)
        return
    
    await session.delete(favorite)
    await session.commit()
    
    await callback.answer(f"✅ {city} удален из избранного")
    
    # Обновить сообщение
    await callback.message.edit_text(
        f"Город {city} удален из избранного.\n\n"
        "Просмотреть избранное: /favorites"
    )


@router.callback_query(F.data.startswith("refresh_weather_"))
async def process_refresh_weather(callback: CallbackQuery):
    """Обновление погоды"""
    city = callback.data.split("_", 2)[2]
    
    await callback.answer("Обновляю погоду...")
    
    weather = await weather_api.get_current_weather(city)
    
    if not weather:
        await callback.message.answer(f"❌ Не удалось получить погоду для '{city}'.")
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
    
    await callback.message.edit_text(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )


@router.callback_query(F.data.startswith("show_forecast_"))
async def process_show_forecast(callback: CallbackQuery):
    """Показать прогноз"""
    city = callback.data.split("_", 2)[2]
    
    await callback.answer("Получаю прогноз...")
    
    forecast = await weather_api.get_forecast(city, 5)
    
    if not forecast:
        await callback.message.answer(f"❌ Не удалось получить прогноз для '{city}'.")
        return
    
    forecast_text = f"📅 Прогноз погоды для {forecast['city']}, {forecast['country']}:\n\n"
    
    for day in forecast['forecast']:
        forecast_text += (
            f"📆 {day['date']}\n"
            f"🌡 {day['temp_min']}°C ... {day['temp_max']}°C\n"
            f"📝 {day['description']}\n\n"
        )
    
    await callback.message.answer(forecast_text)


@router.callback_query(F.data.startswith("weather_favorite_"))
async def process_weather_favorite(callback: CallbackQuery):
    """Показать погоду для избранного города"""
    city = callback.data.split("_", 2)[2]
    
    await callback.answer("Получаю погоду...")
    
    weather = await weather_api.get_current_weather(city)
    
    if not weather:
        await callback.message.answer(f"❌ Не удалось получить погоду для '{city}'.")
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
    
    await callback.message.answer(
        weather_text,
        reply_markup=get_weather_actions_keyboard(city)
    )


@router.callback_query(F.data == "back")
async def process_back(callback: CallbackQuery):
    """Кнопка назад"""
    await callback.answer()
    await callback.message.answer("Используйте /menu для главного меню")


@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery):
    """Кнопка отмены"""
    await callback.answer()
    await callback.message.edit_text("❌ Отменено")
    await callback.message.answer("Используйте /menu для главного меню")
