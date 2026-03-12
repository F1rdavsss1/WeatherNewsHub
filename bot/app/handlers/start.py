"""Обработчики команд start и help"""
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.keyboards.reply import get_main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """
    Обработчик команды /start
    Регистрирует пользователя в БД и отправляет приветствие
    """
    user_id = message.from_user.id
    
    # Проверка существования пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Создание нового пользователя
        user = User(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language="ru"
        )
        session.add(user)
        await session.commit()
        logger.info(f"Зарегистрирован новый пользователь: {user_id}")
    
    # Приветственное сообщение согласно ТЗ
    name = user.first_name or message.from_user.first_name or "друг"
    welcome_text = (
        f"👋 Привет, {name}!\n\n"
        f"🌤️ Я WeatherNews Bot — твой помощник для получения:\n"
        f"• Актуальной информации о погоде\n"
        f"• Последних новостей по категориям\n"
        f"• Ежедневных уведомлений\n\n"
        f"🔐 Вход на сайт: /login\n"
        f"🚀 Начни с команды /weather <город> или /news\n"
        f"📖 Все команды: /help"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    """Обработчик команды /help - полная справка согласно ТЗ"""
    help_text = (
        "📋 Все команды WeatherNews Bot:\n\n"
        
        "🔐 ВХОД НА САЙТ:\n"
        "/login - получить код для входа на сайт\n"
        "Код действителен 5 минут\n\n"
        
        "🌤 ПОГОДА:\n"
        "/weather [город] - текущая погода\n"
        "/forecast [город] [дни] - прогноз на 1-7 дней\n"
        "/setcity [город] - установить город по умолчанию\n"
        "/mycity - погода в сохраненном городе\n\n"
        
        "⭐ ИЗБРАННОЕ:\n"
        "/favorites - список избранных городов\n"
        "/addfavorite [город] - добавить в избранное\n"
        "/removefavorite [город] - удалить из избранного\n\n"
        
        "📰 НОВОСТИ:\n"
        "/news [категория] - топ-5 новостей\n"
        "/categories - список категорий\n\n"
        
        "🔔 ПОДПИСКИ:\n"
        "/subscribe [категория] - подписаться на категорию\n"
        "/unsubscribe [категория] - отписаться\n"
        "/mysubs - мои подписки\n\n"
        
        "⏰ РАССЫЛКИ:\n"
        "/daily [время] - ежедневная рассылка (пример: /daily 09:00)\n"
        "/daily_off - отключить рассылку\n"
        "/digest [время] - дайджест (погода + новости)\n\n"
        
        "ℹ️ ДРУГОЕ:\n"
        "/menu - главное меню\n"
        "/about - информация о боте\n"
        "/feedback [текст] - отправить отзыв\n"
        "/stats - статистика (для админов)\n"
        "/help - эта справка"
    )
    
    await message.answer(help_text)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Показать главное меню"""
    await message.answer(
        "🏠 Главное меню\n\nВыберите действие:",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    """Информация о боте"""
    about_text = (
        "🤖 WeatherNews Bot\n\n"
        "Многофункциональный бот для получения:\n"
        "• 🌤 Актуальной информации о погоде\n"
        "• 📰 Последних новостей по категориям\n"
        "• 🔔 Ежедневных уведомлений\n\n"
        "Технологии:\n"
        "• Python 3.10+ & aiogram 3.x\n"
        "• PostgreSQL & Redis\n"
        "• OpenWeatherMap API\n"
        "• CurrentsAPI\n\n"
        "Версия: 1.0.0\n"
        "Разработано с ❤️"
    )
    await message.answer(about_text)


@router.message(Command("feedback"))
async def cmd_feedback(message: Message):
    """Отправка отзыва"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "Использование: /feedback <текст>\n"
            "Пример: /feedback Отличный бот!"
        )
        return
    
    feedback_text = args[1]
    
    # Отправка отзыва админам
    from app.config import settings
    
    feedback_message = (
        f"📝 Новый отзыв от пользователя:\n\n"
        f"👤 ID: {message.from_user.id}\n"
        f"👤 Username: @{message.from_user.username or 'нет'}\n"
        f"👤 Имя: {message.from_user.first_name}\n\n"
        f"💬 Отзыв:\n{feedback_text}"
    )
    
    from aiogram import Bot
    bot = message.bot
    
    sent_count = 0
    for admin_id in settings.admin_list:
        try:
            await bot.send_message(admin_id, feedback_message)
            sent_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить отзыв админу {admin_id}: {e}")
    
    if sent_count > 0:
        await message.answer("✅ Спасибо за ваш отзыв! Мы его получили.")
    else:
        await message.answer("✅ Спасибо за ваш отзыв!")


@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession):
    """Статистика бота (только для админов)"""
    from app.config import settings
    
    if message.from_user.id not in settings.admin_list:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    # Подсчет статистики
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    total_users = len(users)
    subscribed_users = sum(1 for u in users if u.is_subscribed)
    users_with_city = sum(1 for u in users if u.default_city)
    
    stats_text = (
        f"📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"🔔 С подпиской: {subscribed_users}\n"
        f"🏙 С городом по умолчанию: {users_with_city}"
    )
    
    await message.answer(stats_text)
