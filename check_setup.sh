#!/bin/bash

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Проверка настройки WeatherNews Hub"
echo "======================================"
echo ""

# Проверка Python
echo -n "Python 3.8+: "
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ $VERSION${NC}"
else
    echo -e "${RED}✗ Не установлен${NC}"
fi

# Проверка Node.js
echo -n "Node.js 18+: "
if command -v node &> /dev/null; then
    VERSION=$(node --version)
    echo -e "${GREEN}✓ $VERSION${NC}"
else
    echo -e "${RED}✗ Не установлен${NC}"
fi

# Проверка npm
echo -n "npm: "
if command -v npm &> /dev/null; then
    VERSION=$(npm --version)
    echo -e "${GREEN}✓ $VERSION${NC}"
else
    echo -e "${RED}✗ Не установлен${NC}"
fi

echo ""
echo "📁 Проверка структуры проекта"
echo "======================================"

# Проверка директорий
echo -n "bot/: "
[ -d "bot" ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo -n "front/: "
[ -d "front" ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo -n "start.sh: "
[ -f "start.sh" ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo ""
echo "⚙️  Проверка конфигурации"
echo "======================================"

# Проверка bot/.env
echo -n "bot/.env: "
if [ -f "bot/.env" ]; then
    echo -e "${GREEN}✓ Существует${NC}"
    
    # Проверка BOT_TOKEN
    echo -n "  BOT_TOKEN: "
    if grep -q "^BOT_TOKEN=.\+" bot/.env 2>/dev/null; then
        echo -e "${GREEN}✓ Настроен${NC}"
    else
        echo -e "${YELLOW}⚠ Не настроен${NC}"
    fi
    
    # Проверка WEATHER_API_KEY
    echo -n "  WEATHER_API_KEY: "
    if grep -q "^WEATHER_API_KEY=.\+" bot/.env 2>/dev/null; then
        echo -e "${GREEN}✓ Настроен${NC}"
    else
        echo -e "${YELLOW}⚠ Не настроен (будут демо данные)${NC}"
    fi
    
    # Проверка NEWS_API_KEY
    echo -n "  NEWS_API_KEY: "
    if grep -q "^NEWS_API_KEY=.\+" bot/.env 2>/dev/null; then
        echo -e "${GREEN}✓ Настроен${NC}"
    else
        echo -e "${YELLOW}⚠ Не настроен (будут демо данные)${NC}"
    fi
else
    echo -e "${RED}✗ Не найден${NC}"
fi

# Проверка front/.env
echo -n "front/.env: "
if [ -f "front/.env" ]; then
    echo -e "${GREEN}✓ Существует${NC}"
else
    echo -e "${YELLOW}⚠ Не найден (будет создан при запуске)${NC}"
fi

echo ""
echo "📦 Проверка зависимостей"
echo "======================================"

# Python venv
echo -n "Python venv: "
if [ -d "bot/venv" ]; then
    echo -e "${GREEN}✓ Создано${NC}"
else
    echo -e "${YELLOW}⚠ Не создано (будет создано при запуске)${NC}"
fi

# Node modules
echo -n "Node modules: "
if [ -d "front/node_modules" ]; then
    echo -e "${GREEN}✓ Установлены${NC}"
else
    echo -e "${YELLOW}⚠ Не установлены (будут установлены при запуске)${NC}"
fi

echo ""
echo "🔌 Проверка портов"
echo "======================================"

# Проверка порта 8000
echo -n "Порт 8000 (API): "
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Занят${NC}"
else
    echo -e "${GREEN}✓ Свободен${NC}"
fi

# Проверка порта 5173
echo -n "Порт 5173 (Frontend): "
if lsof -i :5173 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Занят${NC}"
else
    echo -e "${GREEN}✓ Свободен${NC}"
fi

echo ""
echo "======================================"
echo "✨ Готово к запуску!"
echo ""
echo "Запустите: ./start.sh"
echo "Откройте: http://localhost:5173"
echo ""
