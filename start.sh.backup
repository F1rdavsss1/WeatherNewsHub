#!/bin/bash

# Определяем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🌤️  WeatherNews Hub - Запуск всех сервисов          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📂 Рабочая директория: $(pwd)${NC}"
echo ""

# Функция для остановки всех процессов при выходе
cleanup() {
    echo -e "\n${YELLOW}🛑 Остановка всех сервисов...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не найден. Установите Python 3.8+${NC}"
    exit 1
fi

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден. Установите Node.js 18+${NC}"
    exit 1
fi

# Проверка npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm не найден. Установите npm${NC}"
    exit 1
fi

echo -e "${CYAN}📦 Проверка зависимостей...${NC}"

# Проверка структуры проекта
if [ ! -d "bot" ]; then
    echo -e "${RED}❌ Папка bot/ не найдена${NC}"
    echo -e "${YELLOW}Убедитесь, что вы запускаете скрипт из корня проекта${NC}"
    exit 1
fi

if [ ! -d "front" ]; then
    echo -e "${RED}❌ Папка front/ не найдена${NC}"
    echo -e "${YELLOW}Убедитесь, что вы запускаете скрипт из корня проекта${NC}"
    exit 1
fi

# Установка Python зависимостей для API
cd bot
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  Создание виртуального окружения Python...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

echo -e "${CYAN}📦 Установка Python зависимостей для API...${NC}"
pip install -q fastapi uvicorn httpx python-dotenv 2>/dev/null

# Проверка зависимостей для Telegram бота
if [ -f "requirements.txt" ]; then
    echo -e "${CYAN}📦 Установка зависимостей для Telegram бота...${NC}"
    pip install -q -r requirements.txt 2>/dev/null
fi

cd ..

# Установка Node.js зависимостей для фронтенда
cd front
if [ ! -d "node_modules" ]; then
    echo -e "${CYAN}📦 Установка зависимостей для фронтенда...${NC}"
    # Исправляем права доступа если нужно
    if [ -f "package-lock.json" ]; then
        chmod 644 package-lock.json 2>/dev/null || true
    fi
    npm install --legacy-peer-deps 2>/dev/null || npm install
fi
cd ..

echo ""
echo -e "${GREEN}✅ Все зависимости установлены${NC}"
echo ""

# Проверка API ключей
if [ ! -f "bot/.env" ]; then
    echo -e "${YELLOW}⚠️  Файл bot/.env не найден${NC}"
    echo -e "${CYAN}Создаю bot/.env с примером...${NC}"
    cat > bot/.env << 'ENVEOF'
# Telegram Bot (опционально)
BOT_TOKEN=

# API Keys (опционально - для реальных данных)
OPENWEATHER_API_KEY=
NEWS_API_KEY=

# Database
DATABASE_URL=sqlite+aiosqlite:///./bot.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
ENVEOF
    echo -e "${GREEN}✅ Создан bot/.env${NC}"
    echo -e "${CYAN}Для реальных данных добавьте API ключи в bot/.env${NC}"
    echo ""
fi

# Проверка frontend .env
if [ ! -f "front/.env" ]; then
    echo -e "${CYAN}Создаю front/.env...${NC}"
    cat > front/.env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_TELEGRAM_BOT_NAME=weathernews_bot
EOF
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Запуск сервисов...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Создаем директорию для логов
mkdir -p logs

# 1. Запуск API сервера
echo -e "${CYAN}[1/3] 🌐 Запуск API сервера...${NC}"
cd bot
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
python3 api_server.py > ../logs/api.log 2>&1 &
API_PID=$!
cd ..
sleep 2

# Проверка запуска API
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ API сервер запущен на http://localhost:8000${NC}"
else
    echo -e "${YELLOW}   ⚠️  API сервер не запустился (проверьте logs/api.log)${NC}"
    echo -e "${CYAN}   Фронтенд будет использовать mock данные${NC}"
fi

# 2. Запуск Telegram бота (опционально)
echo -e "${CYAN}[2/3] 🤖 Проверка Telegram бота...${NC}"

# Проверяем наличие BOT_TOKEN
BOT_TOKEN_SET=false
if [ -f "bot/.env" ]; then
    if grep -q "^BOT_TOKEN=.\+" bot/.env 2>/dev/null; then
        BOT_TOKEN_SET=true
    fi
fi

if [ "$BOT_TOKEN_SET" = false ]; then
    echo -e "${YELLOW}   ⚠️  BOT_TOKEN не настроен в bot/.env${NC}"
    echo -e "${CYAN}   Telegram бот не будет запущен${NC}"
    echo -e "${CYAN}   Для запуска бота добавьте BOT_TOKEN в bot/.env${NC}"
else
    cd bot
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    # Проверяем наличие Redis
    if command -v redis-cli &> /dev/null && redis-cli ping > /dev/null 2>&1; then
        python3 main.py > ../logs/bot.log 2>&1 &
        BOT_PID=$!
        sleep 2
        echo -e "${GREEN}   ✅ Telegram бот запущен${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Redis не запущен. Telegram бот требует Redis${NC}"
        echo -e "${CYAN}   Установите и запустите Redis: sudo apt install redis-server${NC}"
    fi
    cd ..
fi

# 3. Запуск фронтенда
echo -e "${CYAN}[3/3] 💻 Запуск фронтенда...${NC}"
cd front
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3

# Проверка запуска фронтенда
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Фронтенд запущен на http://localhost:5173${NC}"
else
    echo -e "${RED}   ❌ Фронтенд не запустился (проверьте logs/frontend.log)${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Все сервисы запущены!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${PURPLE}📱 Доступные сервисы:${NC}"
echo ""
echo -e "   ${CYAN}🌐 API Server:${NC}      http://localhost:8000"
echo -e "   ${CYAN}📖 API Docs:${NC}        http://localhost:8000/docs"
echo -e "   ${CYAN}💻 Frontend:${NC}        http://localhost:5173"
if [ ! -z "$BOT_PID" ]; then
    echo -e "   ${CYAN}🤖 Telegram Bot:${NC}    Запущен"
fi
echo ""
echo -e "${PURPLE}📊 Логи:${NC}"
echo ""
echo -e "   ${CYAN}API:${NC}      tail -f logs/api.log"
echo -e "   ${CYAN}Frontend:${NC} tail -f logs/frontend.log"
if [ ! -z "$BOT_PID" ]; then
    echo -e "   ${CYAN}Bot:${NC}      tail -f logs/bot.log"
fi
echo ""
echo -e "${YELLOW}⚠️  Нажмите Ctrl+C для остановки всех сервисов${NC}"
echo ""

# Открываем браузер (опционально)
sleep 2
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173 2>/dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:5173 2>/dev/null &
fi

# Ожидание
wait
