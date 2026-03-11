"""Планировщик задач для рассылки уведомлений"""
import logging
from datetime import datetime, time
from typing import TYPE_CHECKING
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from aiogram import Bot

from app.models.user import User
from app.utils.weather_api import weather_api
from app.utils.news_api import news_api

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Планировщик уведомлений"""
    
    def __init__(self, bot: "Bot", session_maker):
        self.bot = bot
        self.session_maker = session_maker
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Запуск планировщика"""
        # Проверка подписок каждую минуту
        self.scheduler.add_job(
            self._check_notifications,
            trigger=CronTrigger(minute="*"),
            id="check_notifications",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Планировщик уведомлений запущен")
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик уведомлений остановлен")
    
    async def _check_notifications(self):
        """Проверка и отправка уведомлений"""
        current_time = datetime.now().time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        async with self.session_maker() as session:
            # Получение пользователей с подпиской на текущее время
            stmt = select(User).where(
                User.is_subscribed == True,
                User.notification_time != None
            )
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            for user in users:
                if (user.notification_time.hour == current_hour and
                    user.notification_time.minute == current_minute):
                    await self._send_daily_notification(user)
    
    async def _send_daily_notification(self, user: User):
        """
        Отправка ежедневного уведомления пользователю
        
        Args:
            user: Объект пользователя
        """
        try:
            message_parts = ["🌅 Доброе утро! Вот ваша ежедневная сводка:\n"]
            
            # Погода в городе по умолчанию
            if user.default_city:
                weather = await weather_api.get_current_weather(
                    user.default_city,
                    lang=user.language
                )
                if weather:
                    message_parts.append(
                        f"\n🌤 Погода в {weather['city']}:\n"
                        f"🌡 Температура: {weather['temp']}°C (ощущается как {weather['feels_like']}°C)\n"
                        f"📝 {weather['description']}\n"
                        f"💨 Ветер: {weather['wind_speed']} м/с\n"
                        f"💧 Влажность: {weather['humidity']}%"
                    )
            
            # Топ-3 новости
            news = await news_api.get_top_headlines(
                category="general",
                language="ru" if user.language == "ru" else "en",
                page_size=3
            )
            
            if news:
                message_parts.append("\n\n📰 Топ новости дня:")
                for i, article in enumerate(news, 1):
                    message_parts.append(
                        f"\n{i}. {article['title']}\n"
                        f"🔗 {article['url']}"
                    )
            
            message = "\n".join(message_parts)
            await self.bot.send_message(user.telegram_id, message)
            logger.info(f"Отправлено уведомление пользователю {user.telegram_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления пользователю {user.telegram_id}: {e}")
