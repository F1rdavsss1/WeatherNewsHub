# 🌤️ WeatherNews Hub

Современный веб-сайт и Telegram бот для отображения погоды и новостей.

## 🚀 Быстрый запуск

Запустите всё одной командой из корневой директории:

```bash
./start.sh
```

Это запустит:
- ✅ API сервер (http://localhost:8000)
- ✅ Фронтенд (http://localhost:5173)
- ✅ Telegram бот (если настроен BOT_TOKEN)

## 📋 Требования

- Python 3.8+
- Node.js 18+
- npm

## ⚙️ Настройка

### API ключи

Отредактируйте `bot/.env`:

```env
# Telegram бот (обязательно для бота)
BOT_TOKEN=ваш_токен_бота

# API ключи (опционально - для реальных данных)
WEATHER_API_KEY=ваш_ключ_openweather
NEWS_API_KEY=ваш_ключ_newsapi
```

Получить ключи:
- Telegram бот: @BotFather в Telegram
- Погода: https://openweathermap.org/api (бесплатно)
- Новости: https://newsapi.org/register (бесплатно)

### Fallback на демо данные

Если API ключи не настроены, сайт автоматически покажет демо данные.

## 📱 Функции

### Веб-сайт
- ✅ Тёмная тема с фиолетовыми акцентами
- ✅ Текущая погода и прогноз на 7 дней
- ✅ Новости по категориям (без картинок)
- ✅ Поиск городов
- ✅ Адаптивный дизайн

### Telegram Bot
- ✅ Погода по городам
- ✅ Новости по категориям (без картинок)
- ✅ Избранные города
- ✅ Подписки на категории новостей
- ✅ Ежедневные уведомления

## 🌐 Доступные URL

После запуска:
- **Веб-сайт:** http://localhost:5173
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📊 Логи

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

## 📁 Структура проекта

```
WeatherNews Hub/
├── start.sh              # Запуск всех сервисов
├── bot/                  # Backend
│   ├── api_server.py    # FastAPI сервер
│   ├── main.py          # Telegram бот
│   ├── app/             # Обработчики бота
│   └── .env             # Конфигурация
├── front/               # Frontend
│   ├── src/             # React исходники
│   └── .env             # Конфигурация
└── logs/                # Логи
```

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
- aiogram 3 (Telegram bot)
- SQLAlchemy + SQLite

## 🔧 Команды бота

```
/start - Начать работу с ботом
/help - Полная справка по командам

Погода:
/weather [город] - текущая погода
/forecast [город] - прогноз на 7 дней
/mycity - погода в сохраненном городе

Новости:
/news [категория] - топ-5 новостей
/categories - список категорий

Избранное:
/favorites - список избранных городов
/addfavorite [город] - добавить город

Подписки:
/subscribe [категория] - подписаться
/mysubs - мои подписки
/daily [время] - настроить рассылку
```

## 📖 Категории новостей

- 📰 Общие (general)
- 💻 Технологии (technology)
- 🔬 Наука (science)
- ⚽️ Спорт (sports)
- 💼 Бизнес (business)
- 🏥 Здоровье (health)
- 🎭 Развлечения (entertainment)

## 🐛 Troubleshooting

### Порт уже занят

```bash
# Найти процесс
lsof -i :8000
lsof -i :5173

# Остановить
kill -9 <PID>
```

### Проверка логов

```bash
# Последние 50 строк
tail -50 logs/api.log
tail -50 logs/bot.log
tail -50 logs/frontend.log
```

## 📄 Лицензия

MIT

## ✨ Готово!

Запустите `./start.sh` и откройте http://localhost:5173

Приятного использования! 🎉
