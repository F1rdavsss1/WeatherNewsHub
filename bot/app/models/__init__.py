"""Модели базы данных"""
from .base import Base
from .user import User, Favorite, NewsCategory

__all__ = ["Base", "User", "Favorite", "NewsCategory"]
