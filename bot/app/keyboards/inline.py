"""Инлайн-клавиатуры"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_news_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с категориями новостей"""
    builder = InlineKeyboardBuilder()
    
    categories = [
        ("📰 Общие", "news_general"),
        ("💻 Технологии", "news_technology"),
        ("🔬 Наука", "news_science"),
        ("⚽️ Спорт", "news_sports"),
        ("💼 Бизнес", "news_business"),
        ("🏥 Здоровье", "news_health"),
        ("🎭 Развлечения", "news_entertainment"),
    ]
    
    for text, callback_data in categories:
        builder.button(text=text, callback_data=callback_data)
    
    builder.adjust(2)  # 2 кнопки в ряд
    return builder.as_markup()


def get_forecast_keyboard(city: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора прогноза погоды"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📅 3 дня", callback_data=f"forecast_{city}_3")
    builder.button(text="📅 5 дней", callback_data=f"forecast_{city}_5")
    builder.button(text="📅 7 дней", callback_data=f"forecast_{city}_7")
    
    builder.adjust(3)
    return builder.as_markup()


def get_weather_actions_keyboard(city: str) -> InlineKeyboardMarkup:
    """Клавиатура с действиями для погоды"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ В избранное", callback_data=f"add_favorite_{city}")
    builder.button(text="🔄 Обновить", callback_data=f"refresh_weather_{city}")
    builder.button(text="📅 Прогноз", callback_data=f"show_forecast_{city}")
    
    builder.adjust(3)
    return builder.as_markup()


def get_favorites_keyboard(favorites: list) -> InlineKeyboardMarkup:
    """Клавиатура с избранными городами"""
    builder = InlineKeyboardBuilder()
    
    for city in favorites:
        builder.button(text=f"🌤 {city}", callback_data=f"weather_favorite_{city}")
        builder.button(text="❌", callback_data=f"remove_favorite_{city}")
    
    builder.adjust(2)  # Город и кнопка удаления в одном ряду
    return builder.as_markup()


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="back")
    return builder.as_markup()
