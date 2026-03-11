#!/bin/bash

# Переход в директорию скрипта
cd "$(dirname "$0")"

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         TELEGRAM WEATHER & NEWS BOT - ЗАПУСК                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Создание виртуального окружения...${NC}"
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"
    else
        echo -e "${RED}❌ Ошибка создания виртуального окружения${NC}"
        exit 1
    fi
    echo ""
fi

# Установка зависимостей
echo -e "${BLUE}📥 Проверка зависимостей...${NC}"
venv/bin/pip install --quiet aiogram aiohttp python-dotenv 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
else
    echo -e "${YELLOW}⚠️  Некоторые зависимости могут отсутствовать${NC}"
fi
echo ""

# Проверка готовности
echo -e "${BLUE}🔍 Проверка готовности бота...${NC}"
venv/bin/python3 check_setup.py
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Обнаружены проблемы, но попробуем запустить тестовый бот${NC}"
    echo ""
fi

# Запуск бота
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    БОТ ЗАПУСКАЕТСЯ...                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🤖 Бот: @WeatherNewsHubot${NC}"
echo -e "${BLUE}📝 Для остановки нажмите Ctrl+C${NC}"
echo ""
echo -e "${YELLOW}Режим: Тестовый (без БД)${NC}"
echo -e "${YELLOW}Для полной версии с БД используйте: venv/bin/python3 main.py${NC}"
echo ""

# Запуск тестового бота (без БД)
venv/bin/python3 test_bot.py
