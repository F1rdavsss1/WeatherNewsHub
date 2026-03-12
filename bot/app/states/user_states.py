"""Состояния FSM для диалогов с пользователем"""
from aiogram.fsm.state import State, StatesGroup


class WeatherState(StatesGroup):
    """Состояния для работы с погодой"""
    waiting_for_city = State()
    waiting_for_forecast_days = State()


class NewsState(StatesGroup):
    """Состояния для работы с новостями"""
    waiting_for_category = State()


class SettingsState(StatesGroup):
    """Состояния для настроек"""
    waiting_for_city = State()
    waiting_for_time = State()
    waiting_for_favorite_city = State()


class FavoriteState(StatesGroup):
    """Состояния для избранных городов"""
    waiting_for_add = State()
    waiting_for_remove = State()
    waiting_for_setcity = State()


class SubscriptionState(StatesGroup):
    """Состояния для подписок"""
    waiting_for_subscribe = State()
    waiting_for_unsubscribe = State()
    waiting_for_daily_time = State()
