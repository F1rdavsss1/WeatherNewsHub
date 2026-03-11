"""Модели пользователей и связанных данных"""
from datetime import time, datetime
from typing import List, Optional
from sqlalchemy import BigInteger, String, Boolean, Time, ForeignKey, UniqueConstraint, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="ru", nullable=False)
    default_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notification_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_active: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    favorite_cities: Mapped[List["FavoriteCity"]] = relationship(
        "FavoriteCity",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    weather_history: Mapped[List["WeatherHistory"]] = relationship(
        "WeatherHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Для обратной совместимости
    @property
    def is_subscribed(self) -> bool:
        return self.notification_enabled
    
    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class FavoriteCity(Base):
    """Модель избранных городов"""
    __tablename__ = "favorite_cities"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    added_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorite_cities")
    
    # Уникальность пары пользователь-город
    __table_args__ = (
        UniqueConstraint("user_id", "city_name", name="uq_user_city"),
    )
    
    def __repr__(self) -> str:
        return f"<FavoriteCity(user_id={self.user_id}, city={self.city_name})>"


class NewsCategory(Base):
    """Модель категорий новостей"""
    __tablename__ = "news_categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category_name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    category_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    subscriptions: Mapped[List["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<NewsCategory(code={self.category_code}, name_ru={self.category_name_ru})>"


class UserSubscription(Base):
    """Модель подписок пользователей на категории новостей"""
    __tablename__ = "user_subscriptions"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("news_categories.id", ondelete="CASCADE"), primary_key=True)
    subscribed_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    category: Mapped["NewsCategory"] = relationship("NewsCategory", back_populates="subscriptions")
    
    def __repr__(self) -> str:
        return f"<UserSubscription(user_id={self.user_id}, category_id={self.category_id})>"


class WeatherHistory(Base):
    """История запросов погоды"""
    __tablename__ = "weather_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="weather_history")
    
    def __repr__(self) -> str:
        return f"<WeatherHistory(user_id={self.user_id}, city={self.city}, temp={self.temperature})>"


class WeatherCache(Base):
    """Кэш погоды"""
    __tablename__ = "weather_cache"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    weather_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON строка
    fetched_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    
    def __repr__(self) -> str:
        return f"<WeatherCache(city={self.city}, expires_at={self.expires_at})>"


class NewsCache(Base):
    """Кэш новостей"""
    __tablename__ = "news_cache"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(10), nullable=False)
    news_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON строка
    fetched_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    
    def __repr__(self) -> str:
        return f"<NewsCache(category={self.category}, country={self.country})>"


class ActivityLog(Base):
    """Логи активности пользователей"""
    __tablename__ = "activity_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    command: Mapped[str] = mapped_column(String(100), nullable=False)
    parameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # success, error
    response_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # миллисекунды
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="activity_logs")
    
    def __repr__(self) -> str:
        return f"<ActivityLog(user_id={self.user_id}, command={self.command}, status={self.status})>"
