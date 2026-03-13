"""Хранилище кодов авторизации (общее для бота и API)"""
from datetime import datetime, timedelta
from typing import Optional
import random
import string
import sqlite3
import json
import os

# Путь к базе данных
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bot.db')


def _get_connection():
    """Получение подключения к БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_auth_codes_table():
    """Инициализация таблицы кодов авторизации"""
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auth_codes (
                code TEXT PRIMARY KEY,
                user_data TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


# Инициализируем таблицу при импорте модуля
_init_auth_codes_table()


def generate_auth_code() -> str:
    """Генерация 6-значного кода"""
    return ''.join(random.choices(string.digits, k=6))


def save_auth_code(code: str, user_data: dict) -> None:
    """Сохранение кода авторизации"""
    expires_at = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO auth_codes (code, user_data, expires_at) VALUES (?, ?, ?)",
            (code, json.dumps(user_data), expires_at)
        )
        conn.commit()
        print(f"[AUTH_STORAGE] Сохранён код {code} для пользователя {user_data.get('telegram_id')}")
    finally:
        conn.close()


def verify_auth_code(code: str) -> Optional[dict]:
    """Проверка кода авторизации"""
    print(f"[AUTH_STORAGE] Проверка кода: {code}")
    
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT user_data, expires_at FROM auth_codes WHERE code = ?",
            (code,)
        )
        row = cursor.fetchone()
        
        if not row:
            print(f"[AUTH_STORAGE] Код {code} не найден")
            return None
        
        user_data = json.loads(row['user_data'])
        expires_at = datetime.fromisoformat(row['expires_at'])
        
        # Проверка срока действия
        if datetime.now() > expires_at:
            print(f"[AUTH_STORAGE] Код {code} истёк")
            conn.execute("DELETE FROM auth_codes WHERE code = ?", (code,))
            conn.commit()
            return None
        
        # Удаляем использованный код
        print(f"[AUTH_STORAGE] Код {code} валиден, удаляем")
        conn.execute("DELETE FROM auth_codes WHERE code = ?", (code,))
        conn.commit()
        
        return user_data
    finally:
        conn.close()


def cleanup_expired_codes() -> None:
    """Очистка истёкших кодов"""
    conn = _get_connection()
    try:
        now = datetime.now().isoformat()
        conn.execute("DELETE FROM auth_codes WHERE expires_at < ?", (now,))
        deleted = conn.total_changes
        conn.commit()
        if deleted > 0:
            print(f"[AUTH_STORAGE] Удалено истёкших кодов: {deleted}")
    finally:
        conn.close()
