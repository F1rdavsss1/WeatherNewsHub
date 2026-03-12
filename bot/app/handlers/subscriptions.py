"""Обработчики команд подписок на новости"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, NewsCategory, UserSubscription
from app.states.user_states import SubscriptionState
from app.keyboards.inline import get_news_categories_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message, session: AsyncSession, state: FSMContext):
    """Подписаться на категорию новостей"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        # Показать список категорий
        stmt = select(NewsCategory)
        result = await session.execute(stmt)
        categories = result.scalars().all()
        
        text = "📰 Выберите категорию для подписки:\n\n"
        for cat in categories:
            text += f"• {cat.category_name_ru} - /subscribe {cat.category_code}\n"
        
        await message.answer(text, reply_markup=get_news_categories_keyboard())
        await state.set_state(SubscriptionState.waiting_for_subscribe)
        return
    
    category_code = args[1].strip().lower()
    await subscribe_to_category(message, session, category_code)


@router.message(SubscriptionState.waiting_for_subscribe)
async def process_subscribe(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка выбора категории для подписки"""
    category_code = message.text.strip().lower()
    
    if category_code == "❌ отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    await subscribe_to_category(message, session, category_code)
    await state.clear()


async def subscribe_to_category(message: Message, session: AsyncSession, category_code: str):
    """Подписка на категорию"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    # Поиск категории
    stmt = select(NewsCategory).where(NewsCategory.category_code == category_code)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        await message.answer(
            f"❌ Категория '{category_code}' не найдена.\n\n"
            "Доступные категории: /categories"
        )
        return
    
    # Проверка существующей подписки
    stmt = select(UserSubscription).where(
        UserSubscription.user_id == user.id,
        UserSubscription.category_id == category.id
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        await message.answer(f"⚠️ Вы уже подписаны на категорию '{category.category_name_ru}'.")
        return
    
    # Создание подписки
    subscription = UserSubscription(
        user_id=user.id,
        category_id=category.id
    )
    session.add(subscription)
    await session.commit()
    
    await message.answer(
        f"✅ Вы подписались на категорию '{category.category_name_ru}'!\n\n"
        f"Теперь вы будете получать новости из этой категории в ежедневном дайджесте.\n\n"
        f"Просмотреть все подписки: /mysubs"
    )
    logger.info(f"Пользователь {user_id} подписался на категорию {category_code}")


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message, session: AsyncSession, state: FSMContext):
    """Отписаться от категории новостей"""
    args = message.text.split(maxsplit=1)
    
    user_id = message.from_user.id
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    if len(args) < 2:
        # Показать список подписок
        stmt = (
            select(NewsCategory)
            .join(UserSubscription)
            .where(UserSubscription.user_id == user.id)
        )
        result = await session.execute(stmt)
        categories = result.scalars().all()
        
        if not categories:
            await message.answer("У вас нет активных подписок.")
            return
        
        text = "📰 Ваши подписки:\n\n"
        for cat in categories:
            text += f"• {cat.category_name_ru} - /unsubscribe {cat.category_code}\n"
        
        text += "\nОтправьте код категории для отписки."
        await message.answer(text)
        await state.set_state(SubscriptionState.waiting_for_unsubscribe)
        return
    
    category_code = args[1].strip().lower()
    await unsubscribe_from_category(message, session, category_code)


@router.message(SubscriptionState.waiting_for_unsubscribe)
async def process_unsubscribe(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка выбора категории для отписки"""
    category_code = message.text.strip().lower()
    
    if category_code == "❌ отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    await unsubscribe_from_category(message, session, category_code)
    await state.clear()


async def unsubscribe_from_category(message: Message, session: AsyncSession, category_code: str):
    """Отписка от категории"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    # Поиск категории
    stmt = select(NewsCategory).where(NewsCategory.category_code == category_code)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        await message.answer(f"❌ Категория '{category_code}' не найдена.")
        return
    
    # Поиск подписки
    stmt = select(UserSubscription).where(
        UserSubscription.user_id == user.id,
        UserSubscription.category_id == category.id
    )
    result = await session.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        await message.answer(f"⚠️ Вы не подписаны на категорию '{category.category_name_ru}'.")
        return
    
    # Удаление подписки
    await session.delete(subscription)
    await session.commit()
    
    await message.answer(
        f"✅ Вы отписались от категории '{category.category_name_ru}'."
    )
    logger.info(f"Пользователь {user_id} отписался от категории {category_code}")


@router.message(Command("mysubs"))
@router.message(F.text == "📋 Мои подписки")
async def cmd_my_subs(message: Message, session: AsyncSession):
    """Показать мои подписки"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    # Получение подписок
    stmt = (
        select(NewsCategory)
        .join(UserSubscription)
        .where(UserSubscription.user_id == user.id)
    )
    result = await session.execute(stmt)
    categories = result.scalars().all()
    
    if not categories:
        await message.answer(
            "У вас пока нет подписок на новости.\n\n"
            "Подпишитесь на категорию: /subscribe <категория>\n"
            "Доступные категории: /categories"
        )
        return
    
    # Формирование списка
    text = "📋 Ваши подписки на новости:\n\n"
    for i, cat in enumerate(categories, 1):
        text += f"{i}. {cat.category_name_ru} ({cat.category_code})\n"
    
    text += f"\n📊 Всего: {len(categories)} категорий"
    text += "\n\n💡 Вы будете получать новости из этих категорий в ежедневном дайджесте."
    
    await message.answer(text)


@router.message(Command("daily"))
async def cmd_daily(message: Message, session: AsyncSession, state: FSMContext):
    """Настроить ежедневную рассылку"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "Укажите время рассылки в формате HH:MM\n\n"
            "Пример: /daily 09:00\n"
            "Пример: /daily 18:30"
        )
        await state.set_state(SubscriptionState.waiting_for_daily_time)
        return
    
    time_str = args[1].strip()
    await set_daily_notification(message, session, time_str)


@router.message(SubscriptionState.waiting_for_daily_time)
async def process_daily_time(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка ввода времени рассылки"""
    time_str = message.text.strip()
    
    if time_str == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.")
        return
    
    await set_daily_notification(message, session, time_str)
    await state.clear()


async def set_daily_notification(message: Message, session: AsyncSession, time_str: str):
    """Установка времени ежедневной рассылки"""
    user_id = message.from_user.id
    
    # Валидация времени
    try:
        hours, minutes = map(int, time_str.split(':'))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError
        time_formatted = f"{hours:02d}:{minutes:02d}"
    except (ValueError, AttributeError):
        await message.answer(
            "❌ Неверный формат времени.\n\n"
            "Используйте формат HH:MM (например, 09:00 или 18:30)"
        )
        return
    
    # Обновление пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    user.notification_time = time_formatted
    user.notification_enabled = True
    await session.commit()
    
    await message.answer(
        f"✅ Ежедневная рассылка настроена на {time_formatted}!\n\n"
        f"Вы будете получать:\n"
        f"• Погоду в вашем городе\n"
        f"• Новости по вашим подпискам\n\n"
        f"Отключить: /daily_off"
    )
    logger.info(f"Пользователь {user_id} настроил рассылку на {time_formatted}")


@router.message(Command("daily_off"))
async def cmd_daily_off(message: Message, session: AsyncSession):
    """Отключить ежедневную рассылку"""
    user_id = message.from_user.id
    
    # Обновление пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    if not user.notification_enabled:
        await message.answer("⚠️ Ежедневная рассылка уже отключена.")
        return
    
    user.notification_enabled = False
    await session.commit()
    
    await message.answer(
        "✅ Ежедневная рассылка отключена.\n\n"
        "Включить снова: /daily <время>"
    )
    logger.info(f"Пользователь {user_id} отключил рассылку")


@router.message(Command("digest"))
async def cmd_digest(message: Message, session: AsyncSession):
    """Настроить дайджест (алиас для /daily)"""
    await message.answer(
        "💡 Команда /digest работает так же, как /daily\n\n"
        "Используйте: /daily <время>\n"
        "Например: /daily 08:30"
    )
