"""Обработчики настроек пользователя"""
import logging
from datetime import time as dt_time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, FavoriteCity
from app.states.user_states import SettingsState
from app.keyboards.inline import get_favorites_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("setcity"))
async def cmd_setcity(message: Message, session: AsyncSession):
    """Установка города по умолчанию"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("Использование: /setcity <город>\nПример: /setcity Москва")
        return
    
    city = args[1]
    
    # Обновление города пользователя
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        user.default_city = city
        await session.commit()
        await message.answer(f"✅ Город по умолчанию установлен: {city}")
    else:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")


@router.message(Command("subscribe"))
@router.message(Command("daily"))
async def cmd_subscribe(message: Message, session: AsyncSession):
    """Подписка на ежедневную рассылку"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "Использование: /subscribe <HH:MM> или /daily <HH:MM>\n"
            "Пример: /subscribe 08:00\n\n"
            "Вы будете получать ежедневную сводку погоды и новостей в указанное время."
        )
        return
    
    time_str = args[1]
    
    # Парсинг времени
    try:
        hour, minute = map(int, time_str.split(":"))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
        notification_time = dt_time(hour, minute)
    except (ValueError, AttributeError):
        await message.answer("❌ Неверный формат времени. Используйте HH:MM (например, 08:00)")
        return
    
    # Обновление настроек пользователя
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        user.notification_time = notification_time
        user.is_subscribed = True
        await session.commit()
        await message.answer(
            f"✅ Подписка активирована!\n"
            f"Вы будете получать уведомления каждый день в {time_str}."
        )
    else:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")


@router.message(Command("unsubscribe"))
@router.message(Command("daily_off"))
async def cmd_unsubscribe(message: Message, session: AsyncSession):
    """Отписка от рассылки"""
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        user.is_subscribed = False
        await session.commit()
        await message.answer("✅ Вы отписались от ежедневной рассылки.")
    else:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")


@router.message(Command("addfavorite"))
async def cmd_addfavorite(message: Message, session: AsyncSession):
    """Добавить город в избранное"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("Использование: /addfavorite <город>\nПример: /addfavorite Москва")
        return
    
    city = args[1]
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")
        return
    
    # Проверка существования
    stmt = select(Favorite).where(
        Favorite.user_id == user.id,
        Favorite.city_name == city
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        await message.answer(f"Город {city} уже в избранном!")
        return
    
    # Добавление в избранное
    favorite = Favorite(user_id=user.id, city_name=city)
    session.add(favorite)
    await session.commit()
    
    await message.answer(f"✅ {city} добавлен в избранное!")


@router.message(Command("removefavorite"))
async def cmd_removefavorite(message: Message, session: AsyncSession):
    """Удалить город из избранного"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("Использование: /removefavorite <город>\nПример: /removefavorite Москва")
        return
    
    city = args[1]
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")
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
        await message.answer(f"✅ {city} удален из избранного")
    else:
        await message.answer(f"❌ Город {city} не найден в избранном")


@router.message(Command("favorites"))
@router.message(F.text == "⭐️ Избранное")
async def cmd_favorites(message: Message, session: AsyncSession):
    """Список избранных городов"""
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")
        return
    
    # Получение избранных городов
    stmt = select(Favorite).where(Favorite.user_id == user.id)
    result = await session.execute(stmt)
    favorites = result.scalars().all()
    
    if not favorites:
        await message.answer(
            "У вас пока нет избранных городов.\n"
            "Добавьте город в избранное через команду /weather <город>"
        )
        return
    
    cities = [fav.city_name for fav in favorites]
    await message.answer(
        "⭐️ Ваши избранные города:",
        reply_markup=get_favorites_keyboard(cities)
    )


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message, session: AsyncSession):
    """Показать текущие настройки"""
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Ошибка. Используйте /start для регистрации.")
        return
    
    settings_text = "⚙️ Ваши настройки:\n\n"
    settings_text += f"🏙 Город по умолчанию: {user.default_city or 'не установлен'}\n"
    settings_text += f"🔔 Подписка: {'активна' if user.is_subscribed else 'неактивна'}\n"
    
    if user.notification_time:
        settings_text += f"⏰ Время уведомлений: {user.notification_time.strftime('%H:%M')}\n"
    
    settings_text += "\n📝 Команды для изменения:\n"
    settings_text += "/setcity <город> - установить город\n"
    settings_text += "/subscribe <HH:MM> - подписаться на рассылку\n"
    settings_text += "/unsubscribe - отписаться от рассылки"
    
    await message.answer(settings_text)
