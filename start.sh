#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🌤️  WeatherNews Hub - Запуск всех сервисов          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📂 Рабочая директория: $(pwd)${NC}"
echo ""

cleanup() {
    echo -e "\n${YELLOW}🛑 Остановка всех сервисов...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не найден${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm не найден${NC}"
    exit 1
fi

echo -e "${CYAN}📦 Проверка зависимостей...${NC}"

if [ ! -d "bot" ] || [ ! -d "front" ]; then
    echo -e "${RED}❌ Папки bot/ или front/ не найдены${NC}"
    exit 1
fi

cd bot
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pip install -q fastapi uvicorn httpx python-dotenv 2>/dev/null

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt 2>/dev/null
fi

cd ../front
if [ ! -d "node_modules" ]; then
    echo -e "${CYAN}📦 Установка зависимостей фронтенда...${NC}"
    npm install --legacy-peer-deps 2>/dev/null || npm install
fi
cd ..

echo -e "${GREEN}✅ Зависимости установлены${NC}"
echo ""

if [ ! -f "bot/.env" ]; then
    cat > bot/.env << 'ENVEOF'
BOT_TOKEN=
WEATHER_API_KEY=
NEWS_API_KEY=
ENVEOF
fi

if [ ! -f "front/.env" ]; then
    cat > front/.env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Запуск сервисов...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

mkdir -p logs

echo -e "${CYAN}[1/3] 🌐 Запуск API сервера...${NC}"
cd bot
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
python3 api_server.py > ../logs/api.log 2>&1 &
API_PID=$!
cd ..
sleep 2

if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ API сервер запущен на http://localhost:8000${NC}"
else
    echo -e "${YELLOW}   ⚠️  API сервер не запустился${NC}"
fi

echo -e "${CYAN}[2/3] 🤖 Telegram бот...${NC}"

BOT_TOKEN_SET=false
if [ -f "bot/.env" ] && grep -q "^BOT_TOKEN=.\+" bot/.env 2>/dev/null; then
    BOT_TOKEN_SET=true
fi

if [ "$BOT_TOKEN_SET" = false ]; then
    echo -e "${YELLOW}   ⚠️  BOT_TOKEN не настроен в bot/.env${NC}"
    echo -e "${CYAN}   Telegram бот не будет запущен${NC}"
else
    cd bot
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    python3 main.py > ../logs/bot.log 2>&1 &
    BOT_PID=$!
    cd ..
    sleep 3
    
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Telegram бот запущен (PID: $BOT_PID)${NC}"
    else
        echo -e "${RED}   ❌ Бот не запустился (см. logs/bot.log)${NC}"
    fi
fi

echo -e "${CYAN}[3/3] 💻 Фронтенд...${NC}"
cd front
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Фронтенд запущен на http://localhost:5173${NC}"
else
    echo -e "${RED}   ❌ Фронтенд не запустился${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Все сервисы запущены!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${PURPLE}📱 Доступные сервисы:${NC}"
echo ""
echo -e "   ${CYAN}🌐 API:${NC}      http://localhost:8000"
echo -e "   ${CYAN}📖 Docs:${NC}     http://localhost:8000/docs"
echo -e "   ${CYAN}💻 Сайт:${NC}     http://localhost:5173"
if [ ! -z "$BOT_PID" ]; then
    echo -e "   ${CYAN}🤖 Бот:${NC}      Запущен (PID: $BOT_PID)"
fi
echo ""
echo -e "${PURPLE}📊 Логи:${NC}"
echo -e "   ${CYAN}tail -f logs/api.log${NC}"
echo -e "   ${CYAN}tail -f logs/frontend.log${NC}"
echo -e "   ${CYAN}tail -f logs/bot.log${NC}"
echo ""
echo -e "${YELLOW}⚠️  Нажмите Ctrl+C для остановки всех сервисов${NC}"
echo ""

sleep 2
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173 2>/dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:5173 2>/dev/null &
fi

wait
