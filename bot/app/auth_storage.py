"""Хранилище кодов авторизации (общее для бота и API)"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import random
import string

# Хранилище одноразовых кодов (в продакшене использовать Redis)
auth_codes: Dict[str, dict] = {}


def generate_auth_code() -> str:
    """Генерация 6-значного кода"""
    return ''.join(random.choices(string.digits, k=6))


def save_auth_code(code: str, user_data: dict) -> None:
    """Сохранение кода авторизации"""
    auth_codes[code] = {
        **user_data,
        'expires_at': datetime.now() + timedelta(minutes=5)
    }
    print(f"[AUTH_STORAGE] Сохранён код {code} для пользователя {user_data.get('telegram_id')}")
    print(f"[AUTH_STORAGE] Всего кодов в хранилище: {len(auth_codes)}")


def verify_auth_code(code: str) -> Optional[dict]:
    """Проверка кода авторизации"""
    print(f"[AUTH_STORAGE] Проверка кода: {code}")
    print(f"[AUTH_STORAGE] Доступные коды: {list(auth_codes.keys())}")
    
    if code not in auth_codes:
        print(f"[AUTH_STORAGE] Код {code} не найден")
        return None
    
    data = auth_codes[code]
    
    # Проверка срока действия
    if datetime.now() > data['expires_at']:
        print(f"[AUTH_STORAGE] Код {code} истёк")
        del auth_codes[code]
        return None
    
    # Удаляем использованный код
    print(f"[AUTH_STORAGE] Код {code} валиден, удаляем")
    del auth_codes[code]
    
    return data


def cleanup_expired_codes() -> None:
    """Очистка истёкших кодов"""
    now = datetime.now()
    expired = [code for code, data in auth_codes.items() if now > data['expires_at']]
    for code in expired:
        del auth_codes[code]
