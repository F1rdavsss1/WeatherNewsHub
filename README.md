<<<<<<< HEAD
# 🌤️ WeatherNews Hub

Современный веб-сайт для отображения погоды и новостей с Telegram ботом.

## ✅ Последние обновления (12 марта 2026)

- ✅ Исправлена загрузка API ключей из `.env`
- ✅ Погода и новости теперь показывают реальные данные
- ✅ Добавлен автоматический fallback на демо данные
- ✅ Улучшена документация и инструкции

**Подробнее:** См. `ИСПРАВЛЕНО.md`

---

## 🚀 Быстрый запуск

### Вариант 1: Всё вместе (рекомендуется)

```bash
./start.sh
```

Запустит:
- ✅ API сервер (http://localhost:8000)
- ✅ Фронтенд (http://localhost:5173)
- ✅ Telegram бот (если настроен)

### Вариант 2: Только веб-сайт (без Telegram бота)

```bash
./start_simple.sh
```

Запустит:
- ✅ API сервер (http://localhost:8000)
- ✅ Фронтенд (http://localhost:5173)

## 📋 Требования

- Python 3.8+
- Node.js 18+
- npm

## ⚙️ Настройка (опционально)

### API ключи (уже настроены!)

✅ API ключи уже добавлены в `bot/.env`:
- Погода: OpenWeatherMap API
- Новости: NewsAPI

Сайт работает с реальными данными!

Если нужно изменить ключи, отредактируйте `bot/.env`:

```env
# Для реальной погоды (бесплатно)
WEATHER_API_KEY=ваш_ключ
# Получить: https://openweathermap.org/api

# Для реальных новостей (бесплатно)
NEWS_API_KEY=ваш_ключ
# Получить: https://newsapi.org/register

# Для Telegram бота (опционально)
BOT_TOKEN=ваш_токен_бота
# Получить: @BotFather в Telegram
```

### Fallback на демо данные

Если API недоступен, сайт автоматически покажет демо данные:
- Погода: Москва, +5°C
- Прогноз: 7 дней
- Новости: 6 статей

## 📱 Что включено

### Веб-сайт (Frontend)
- ✅ Тёмная тема с фиолетовыми акцентами
- ✅ Адаптивный дизайн (mobile, tablet, desktop)
- ✅ Текущая погода и прогноз на 7 дней
- ✅ Лента новостей с фильтрами
- ✅ Поиск городов
- ✅ Авторизация и личный кабинет

### API Server
- ✅ FastAPI сервер
- ✅ Интеграция с OpenWeatherMap
- ✅ Интеграция с NewsAPI
- ✅ CORS для фронтенда
- ✅ Документация: http://localhost:8000/docs

### Telegram Bot (опционально)
- ✅ Получение погоды
- ✅ Получение новостей
- ✅ Подписки и уведомления
- ✅ Настройки пользователя

## 🌐 Доступные URL

После запуска:

- **Веб-сайт:** http://localhost:5173
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📊 Логи

Логи сохраняются в папке `logs/`:

```bash
# API сервер
tail -f logs/api.log

# Фронтенд
tail -f logs/frontend.log

# Telegram бот
tail -f logs/bot.log
```

## 🛑 Остановка

Нажмите `Ctrl+C` в терминале где запущен `start.sh`

Все сервисы остановятся автоматически.

## 📁 Структура проекта

```
WeatherNews Hub/
├── start.sh              # Запуск всех сервисов
├── start_simple.sh       # Запуск без Telegram бота
├── bot/                  # Backend
│   ├── api_server.py    # FastAPI сервер
│   ├── main.py          # Telegram бот
│   └── .env             # Конфигурация
├── front/               # Frontend
│   ├── src/             # Исходники React
│   └── .env             # Конфигурация
└── logs/                # Логи (создаётся автоматически)
```

## 🔧 Ручной запуск (для разработки)

### API сервер:
```bash
cd bot
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn httpx python-dotenv
python api_server.py
```

### Фронтенд:
```bash
cd front
npm install
npm run dev
```

### Telegram бот:
```bash
cd bot
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🐛 Troubleshooting

### Порт уже занят

Если порт 8000 или 5173 занят:

```bash
# Найти процесс
lsof -i :8000
lsof -i :5173

# Остановить
kill -9 <PID>
```

### API не запускается

Проверьте:
1. Python 3.8+ установлен: `python3 --version`
2. Зависимости установлены: `pip list | grep fastapi`
3. Логи: `cat logs/api.log`

### Фронтенд не запускается

Проверьте:
1. Node.js 18+ установлен: `node --version`
2. Зависимости установлены: `ls front/node_modules`
3. Логи: `cat logs/frontend.log`

### Telegram бот не запускается

Проверьте:
1. BOT_TOKEN настроен в `bot/.env`
2. Redis запущен: `redis-cli ping`
3. Логи: `cat logs/bot.log`

## 📖 Документация

- `БЫСТРЫЙ_СТАРТ.md` - Запуск в одну команду
- `ЗАПУСК.txt` - Подробная инструкция по запуску
- `ИСПРАВЛЕНО.md` - Список всех исправлений и улучшений
- `bot/README.md` - Документация backend
- `front/README.md` - Документация фронтенда

## 🎨 Технологии

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Query
- Zustand

**Backend:**
- FastAPI
- Python 3.8+
- httpx

**Telegram Bot:**
- aiogram 3
- SQLAlchemy
- Redis

## 📄 Лицензия

MIT

## 🤝 Поддержка

Если возникли проблемы:
1. Проверьте логи в папке `logs/`
2. Убедитесь, что все зависимости установлены
3. Проверьте, что порты 8000 и 5173 свободны

## ✨ Готово!

Запустите `./start.sh` и откройте http://localhost:5173

Приятного использования! 🎉
=======
# WeatherNewsHub
>>>>>>> fb7f5e8e34105614420029f47a69aae6a9302630
