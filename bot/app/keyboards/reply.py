"""Reply-клавиатуры"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню"""
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="🌤 Погода")
    builder.button(text="📰 Новости")
    builder.button(text="⭐️ Избранное")
    builder.button(text="⚙️ Настройки")
    builder.button(text="ℹ️ Помощь")
    
    builder.adjust(2, 2, 1)  # 2-2-1 расположение кнопок
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)
