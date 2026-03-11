"""Middleware для ограничения частоты запросов"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для защиты от спама"""
    
    def __init__(self, redis_client: aioredis.Redis, throttle_time: int = None):
        super().__init__()
        self.redis = redis_client
        self.throttle_time = throttle_time or settings.THROTTLE_TIME
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Применяем только к сообщениям
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id
        key = f"throttle:{user_id}"
        
        # Проверка наличия ключа
        if await self.redis.exists(key):
            logger.warning(f"Throttling user {user_id}")
            await event.answer("⏳ Пожалуйста, подождите немного перед следующим запросом.")
            return
        
        # Установка ключа с TTL
        await self.redis.setex(key, self.throttle_time, "1")
        
        return await handler(event, data)
