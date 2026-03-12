"""Инициализация обработчиков"""
from aiogram import Router
from . import start, weather, news, settings, callbacks, favorites, subscriptions, auth


def setup_routers() -> Router:
    """Настройка всех роутеров"""
    router = Router()
    
    # Порядок важен - более специфичные обработчики должны быть первыми
    router.include_router(start.router)
    router.include_router(auth.router)
    router.include_router(favorites.router)
    router.include_router(subscriptions.router)
    router.include_router(weather.router)
    router.include_router(news.router)
    router.include_router(settings.router)
    router.include_router(callbacks.router)
    
    return router
