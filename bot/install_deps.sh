#!/bin/bash

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           УСТАНОВКА ЗАВИСИМОСТЕЙ                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Обновление pip
echo -e "${BLUE}📦 Обновление pip...${NC}"
venv/bin/pip install --upgrade pip setuptools wheel

echo ""
echo -e "${BLUE}📥 Установка зависимостей (это может занять время)...${NC}"
echo ""

# Устанавливаем по группам, чтобы избежать конфликтов
echo -e "${YELLOW}[1/4] Основные пакеты...${NC}"
venv/bin/pip install aiogram python-dotenv

echo -e "${YELLOW}[2/4] База данных...${NC}"
venv/bin/pip install sqlalchemy asyncpg alembic

echo -e "${YELLOW}[3/4] Кэширование и планировщик...${NC}"
venv/bin/pip install redis apscheduler

echo -e "${YELLOW}[4/4] Настройки...${NC}"
venv/bin/pip install pydantic-settings

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✅ УСТАНОВКА ЗАВЕРШЕНА                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка
echo -e "${BLUE}🔍 Проверка установленных пакетов:${NC}"
venv/bin/pip list | grep -E "aiogram|aiohttp|sqlalchemy|asyncpg|redis|alembic|apscheduler|pydantic"

echo ""
echo -e "${GREEN}Готово! Теперь можете запустить бота:${NC}"
echo -e "  ${BLUE}./start.sh${NC}          - тестовый режим"
echo -e "  ${BLUE}./start_full.sh${NC}     - полная версия"
echo ""
