#!/usr/bin/env python3
"""Тест авторизации через Telegram код"""
import sys
sys.path.insert(0, 'bot')

from app.auth_storage import generate_auth_code, save_auth_code, verify_auth_code
import requests
import time

print("🧪 Тест системы авторизации\n")

# 1. Генерируем код (как бот)
print("1️⃣ Генерация кода авторизации...")
code = generate_auth_code()
print(f"   Код: {code}")

# 2. Сохраняем код (как бот)
print("\n2️⃣ Сохранение кода в БД...")
user_data = {
    'user_id': 123456,
    'telegram_id': 123456,
    'username': 'test_user',
    'first_name': 'Test'
}
save_auth_code(code, user_data)
print("   ✅ Код сохранён")

# 3. Пропускаем прямую проверку, чтобы не удалить код
print("\n3️⃣ Код готов для проверки через API...")

# 4. Отправляем запрос на API (как фронтенд)
print("\n4️⃣ Отправка запроса на API...")
time.sleep(1)  # Небольшая задержка

try:
    response = requests.post(
        'http://localhost:8000/auth/telegram',
        json={'code': code},
        timeout=5
    )
    
    print(f"   Статус: {response.status_code}")
    data = response.json()
    print(f"   Ответ: {data}")
    
    if data.get('success'):
        print("\n✅ УСПЕХ! Авторизация работает!")
        print(f"   Пользователь: {data.get('user')}")
    else:
        print(f"\n❌ ОШИБКА: {data.get('message')}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Ошибка запроса: {e}")
    sys.exit(1)

print("\n🎉 Все тесты пройдены!")
