"""Обработчики авторизации через Telegram"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.auth_storage import generate_auth_code, save_auth_code

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("login"))
@router.message(F.text == "🔐 Вход на сайт")
async def cmd_login(message: Message, session: AsyncSession):
    """Генерация кода для входа на сайт"""
    user_id = message.from_user.id
    
    # Получение пользователя
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "❌ Сначала используйте /start для регистрации"
        )
        return
    
    # Генерация кода
    code = generate_auth_code()
    
    # Сохранение кода
    save_auth_code(code, {
        'user_id': user_id,
        'telegram_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
    })
    
    await message.answer(
        f"🔐 Ваш код для входа на сайт:\n\n"
        f"<code>{code}</code>\n\n"
        f"⏱ Код действителен 5 минут\n"
        f"🌐 Введите его на сайте: http://localhost:5173/login",
        parse_mode="HTML"
    )
    
    logger.info(f"Сгенерирован код {code} для пользователя {user_id}")
