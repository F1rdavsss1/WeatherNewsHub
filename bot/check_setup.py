#!/usr/bin/env python3
"""Скрипт проверки готовности бота к запуску"""
import sys
import os
from pathlib import Path

# Цвета для вывода
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_header(text):
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{text:^60}{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

def check_python_version():
    """Проверка версии Python"""
    print(f"{BLUE}Проверка версии Python...{NC}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"{GREEN}✅ Python {version.major}.{version.minor}.{version.micro}{NC}")
        return True
    else:
        print(f"{RED}❌ Требуется Python 3.10+, установлено {version.major}.{version.minor}{NC}")
        return False

def check_env_file():
    """Проверка .env файла"""
    print(f"\n{BLUE}Проверка .env файла...{NC}")
    if not Path('.env').exists():
        print(f"{RED}❌ Файл .env не найден{NC}")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    required_vars = ['BOT_TOKEN', 'WEATHER_API_KEY', 'NEWS_API_KEY']
    missing = []
    
    for var in required_vars:
        if var not in content or f'{var}=' not in content:
            missing.append(var)
    
    if missing:
        print(f"{RED}❌ Отсутствуют переменные: {', '.join(missing)}{NC}")
        return False
    
    print(f"{GREEN}✅ Файл .env настроен{NC}")
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    print(f"\n{BLUE}Проверка зависимостей...{NC}")
    
    required = {
        'aiogram': 'aiogram',
        'aiohttp': 'aiohttp',
        'sqlalchemy': 'sqlalchemy',
        'asyncpg': 'asyncpg',
        'redis': 'redis',
        'apscheduler': 'apscheduler',
        'alembic': 'alembic',
        'python-dotenv': 'dotenv'
    }
    
    missing = []
    installed = []
    
    for package, import_name in required.items():
        try:
            __import__(import_name)
            installed.append(package)
            print(f"{GREEN}✅ {package}{NC}")
        except ImportError:
            missing.append(package)
            print(f"{RED}❌ {package}{NC}")
    
    if missing:
        print(f"\n{YELLOW}Установите недостающие пакеты:{NC}")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_structure():
    """Проверка структуры проекта"""
    print(f"\n{BLUE}Проверка структуры проекта...{NC}")
    
    required_dirs = [
        'app',
        'app/handlers',
        'app/keyboards',
        'app/middlewares',
        'app/models',
        'app/states',
        'app/utils',
        'migrations'
    ]
    
    required_files = [
        'main.py',
        'test_bot.py',
        'requirements.txt',
        'app/config.py',
        'app/handlers/__init__.py',
        'app/handlers/start.py',
        'app/handlers/weather.py',
        'app/handlers/news.py',
        'app/handlers/settings.py',
        'app/handlers/callbacks.py',
        'app/utils/weather_api.py',
        'app/utils/news_api.py',
        'app/utils/scheduler.py',
        'app/models/base.py',
        'app/models/user.py'
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            print(f"{GREEN}✅ {dir_path}/{NC}")
        else:
            print(f"{RED}❌ {dir_path}/{NC}")
            all_ok = False
    
    for file_path in required_files:
        if Path(file_path).is_file():
            print(f"{GREEN}✅ {file_path}{NC}")
        else:
            print(f"{RED}❌ {file_path}{NC}")
            all_ok = False
    
    return all_ok

def check_config():
    """Проверка конфигурации"""
    print(f"\n{BLUE}Проверка конфигурации...{NC}")
    
    try:
        from app.config import settings
        
        print(f"{GREEN}✅ BOT_TOKEN: {settings.BOT_TOKEN[:10]}...{NC}")
        print(f"{GREEN}✅ WEATHER_API_KEY: {settings.WEATHER_API_KEY[:10]}...{NC}")
        print(f"{GREEN}✅ NEWS_API_KEY: {settings.NEWS_API_KEY[:10]}...{NC}")
        print(f"{GREEN}✅ Database URL: {settings.database_url.split('@')[0]}@...{NC}")
        print(f"{GREEN}✅ Redis URL: {settings.redis_url}{NC}")
        
        return True
    except Exception as e:
        print(f"{RED}❌ Ошибка загрузки конфигурации: {e}{NC}")
        return False

def main():
    """Главная функция"""
    print_header("ПРОВЕРКА ГОТОВНОСТИ БОТА")
    
    os.chdir(Path(__file__).parent)
    
    checks = [
        ("Python версия", check_python_version),
        (".env файл", check_env_file),
        ("Зависимости", check_dependencies),
        ("Структура проекта", check_structure),
        ("Конфигурация", check_config)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"{RED}❌ Ошибка при проверке {name}: {e}{NC}")
            results.append((name, False))
    
    # Итоги
    print_header("РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASSED{NC}" if result else f"{RED}❌ FAILED{NC}"
        print(f"{name:.<40} {status}")
    
    print(f"\n{BLUE}{'='*60}{NC}")
    if passed == total:
        print(f"{GREEN}🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! ({passed}/{total}){NC}")
        print(f"\n{GREEN}Бот готов к запуску!{NC}")
        print(f"\n{YELLOW}Запустите бота:{NC}")
        print(f"  • Тестовый режим (без БД): {BLUE}python test_bot.py{NC}")
        print(f"  • Полная версия: {BLUE}python main.py{NC}")
        print(f"  • Docker: {BLUE}docker-compose up -d{NC}")
    else:
        print(f"{RED}❌ ПРОВЕРКИ НЕ ПРОЙДЕНЫ ({passed}/{total}){NC}")
        print(f"\n{YELLOW}Исправьте ошибки выше и запустите снова{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
