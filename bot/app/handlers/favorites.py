"""Обработчики команд избранных городов"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, FavoriteCity
from app.states.user_states import FavoriteState
from app.keyboards.inline import get_favorites_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("favorites"))
@router.message(F.text == "⭐ Избранное")
async def cmd_favorites(message: Message, session: AsyncSession):
    """Список избранных городов"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    # Получение избранных городов
    stmt = select(FavoriteCity).where(FavoriteCity.user_id == user.id)
    result = await session.execute(stmt)
    favorites = result.scalars().all()
    
    if not favorites:
        await message.answer(
            "У вас пока нет избранных городов.\n\n"
            "Добавьте город: /addfavorite <город>\n"
            "Например: /addfavorite Москва"
        )
        return
    
    # Формирование списка
    text = "⭐ Ваши избранные города:\n\n"
    for i, fav in enumerate(favorites, 1):
        country = f", {fav.country_code}" if fav.country_code else ""
        text += f"{i}. {fav.city_name}{country}\n"
    
    text += f"\n📊 Всего: {len(favorites)} городов"
    
    await message.answer(text, reply_markup=get_favorites_keyboard([f.city_name for f in favorites]))


@router.message(Command("addfavorite"))
async def cmd_add_favorite(message: Message, session: AsyncSession, state: FSMContext):
    """Добавить город в избранное"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "Укажите название города:\n"
            "/addfavorite <город>\n\n"
            "Пример: /addfavorite Санкт-Петербург"
        )
        await state.set_state(FavoriteState.waiting_for_add)
        return
    
    city_name = args[1].strip()
    await add_favorite_city(message, session, city_name)


@router.message(FavoriteState.waiting_for_add)
async def process_add_favorite(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка ввода города для добавления"""
    city_name = message.text.strip()
    
    if city_name == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    await add_favorite_city(message, session, city_name)
    await state.clear()


async def add_favorite_city(message: Message, session: AsyncSession, city_name: str):
    """Добавление города в избранное"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    # Проверка существования города в избранном
    stmt = select(FavoriteCity).where(
        FavoriteCity.user_id == user.id,
        FavoriteCity.city_name == city_name
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        await message.answer(f"⚠️ Город '{city_name}' уже в избранном.")
        return
    
    # Проверка существования города через API погоды
    from app.utils.weather_api import weather_api
    weather = await weather_api.get_current_weather(city_name)
    
    if not weather:
        await message.answer(
            f"❌ Город '{city_name}' не найден.\n"
            "Проверьте правильность написания."
        )
        return
    
    # Добавление в избранное
    favorite = FavoriteCity(
        user_id=user.id,
        city_name=weather.get('city', city_name),
        country_code=weather.get('country'),
        lat=weather.get('lat'),
        lon=weather.get('lon')
    )
    session.add(favorite)
    await session.commit()
    
    await message.answer(
        f"✅ Город '{weather['city']}' добавлен в избранное!\n\n"
        f"Просмотреть все: /favorites"
    )
    logger.info(f"Пользователь {user_id} добавил город {city_name} в избранное")


@router.message(Command("removefavorite"))
async def cmd_remove_favorite(message: Message, session: AsyncSession, state: FSMContext):
    """Удалить город из избранного"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        # Показать список для выбора
        user_id = message.from_user.id
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return
        
        stmt = select(FavoriteCity).where(FavoriteCity.user_id == user.id)
        result = await session.execute(stmt)
        favorites = result.scalars().all()
        
        if not favorites:
            await message.answer("У вас нет избранных городов.")
            return
        
        text = "Выберите город для удаления:\n\n"
        for i, fav in enumerate(favorites, 1):
            text += f"{i}. {fav.city_name}\n"
        
        text += "\nОтправьте название города или номер."
        await message.answer(text)
        await state.set_state(FavoriteState.waiting_for_remove)
        return
    
    city_name = args[1].strip()
    await remove_favorite_city(message, session, city_name)


@router.message(FavoriteState.waiting_for_remove)
async def process_remove_favorite(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка ввода города для удаления"""
    text = message.text.strip()
    
    if text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    # Проверка, если это номер
    user_id = message.from_user.id
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if text.isdigit():
        index = int(text) - 1
        stmt = select(FavoriteCity).where(FavoriteCity.user_id == user.id)
        result = await session.execute(stmt)
        favorites = result.scalars().all()
        
        if 0 <= index < len(favorites):
            city_name = favorites[index].city_name
        else:
            await message.answer("❌ Неверный номер.")
            return
    else:
        city_name = text
    
    await remove_favorite_city(message, session, city_name)
    await state.clear()


async def remove_favorite_city(message: Message, session: AsyncSession, city_name: str):
    """Удаление города из избранного"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    # Поиск города в избранном
    stmt = select(FavoriteCity).where(
        FavoriteCity.user_id == user.id,
        FavoriteCity.city_name == city_name
    )
    result = await session.execute(stmt)
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        await message.answer(f"❌ Город '{city_name}' не найден в избранном.")
        return
    
    # Удаление
    await session.delete(favorite)
    await session.commit()
    
    await message.answer(f"✅ Город '{city_name}' удален из избранного.")
    logger.info(f"Пользователь {user_id} удалил город {city_name} из избранного")


@router.message(Command("setcity"))
async def cmd_set_city(message: Message, session: AsyncSession, state: FSMContext):
    """Установить город по умолчанию"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "Укажите название города:\n"
            "/setcity <город>\n\n"
            "Пример: /setcity Москва"
        )
        await state.set_state(FavoriteState.waiting_for_setcity)
        return
    
    city_name = args[1].strip()
    await set_default_city(message, session, city_name)


@router.message(FavoriteState.waiting_for_setcity)
async def process_set_city(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка ввода города по умолчанию"""
    city_name = message.text.strip()
    
    if city_name == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    await set_default_city(message, session, city_name)
    await state.clear()


async def set_default_city(message: Message, session: AsyncSession, city_name: str):
    """Установка города по умолчанию"""
    user_id = message.from_user.id
    
    # Проверка существования города
    from app.utils.weather_api import weather_api
    weather = await weather_api.get_current_weather(city_name)
    
    if not weather:
        await message.answer(
            f"❌ Город '{city_name}' не найден.\n"
            "Проверьте правильность написания."
        )
        return
    
    # Обновление пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    user.default_city = weather['city']
    await session.commit()
    
    await message.answer(
        f"✅ Город по умолчанию установлен: {weather['city']}, {weather['country']}\n\n"
        f"Теперь команда /mycity будет показывать погоду в этом городе."
    )
    logger.info(f"Пользователь {user_id} установил город по умолчанию: {weather['city']}")
