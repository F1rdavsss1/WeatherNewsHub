# 🤖 Telegram Бот Погоды и Новостей

Многофункциональный Telegram бот на Python с использованием aiogram 3.x для получения информации о погоде и новостях.

## 🚀 Быстрый старт

### Вариант 1: Простой запуск (рекомендуется для начала)

```bash
# 1. Активируйте виртуальное окружение
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 2. Установите минимальные зависимости (если еще не установлены)
pip install aiogram aiohttp python-dotenv

# 3. Запустите тестовый бот (без БД)
python test_bot.py
```

### Вариант 2: Полная версия с БД

```bash
# 1. Установите PostgreSQL и Redis
sudo apt install postgresql redis-server  # Ubuntu/Debian
# или
brew install postgresql redis             # macOS

# 2. Запустите сервисы
sudo systemctl start postgresql redis     # Linux
# или
brew services start postgresql redis      # macOS

# 3. Создайте базу данных
sudo -u postgres psql
CREATE DATABASE telegram_bot;
\q

# 4. Установите все зависимости
pip install -r requirements.txt

# 5. Примените миграции
alembic upgrade head

# 6. Запустите бота
python main.py
```

### Вариант 3: Docker (самый простой)

```bash
# Запуск всех сервисов одной командой
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
```

## 📋 Возможности

### 🌤 Погода
- Текущая погода в любом городе
- Прогноз погоды на 1-7 дней
- Установка города по умолчанию
- Избранные города для быстрого доступа
- Интерактивные кнопки (обновить, прогноз, в избранное)

### 📰 Новости
- Топ-5 новостей по категориям
- 7 категорий: общие, технологии, наука, спорт, бизнес, здоровье, развлечения
- Интерактивный выбор категорий

### 🔔 Уведомления
- Ежедневная рассылка погоды и новостей
- Настраиваемое время уведомлений
- Персонализированный контент

## 🎯 Команды бота

### Основные команды
```
/start          - Запуск и регистрация
/help           - Справка по командам
```

### Погода
```
/weather <город>        - Текущая погода
/forecast <город> [дни] - Прогноз на 1-7 дней
/setcity <город>        - Установить город по умолчанию
```

Примеры:
```
/weather Москва
/weather London
/forecast Москва 5
/setcity Москва
```

### Новости
```
/news [категория]       - Топ-5 новостей
```

Категории: general, technology, science, sports, business, health

Примеры:
```
/news
/news technology
/news sports
```

### Настройки
```
/subscribe <HH:MM>      - Подписка на ежедневную рассылку
/unsubscribe            - Отписка от рассылки
/favorites              - Избранные города
```

Примеры:
```
/subscribe 08:00
/favorites
```

### Админ команды
```
/stats                  - Статистика бота (только для админов)
```

## 🔑 Настройка API ключей

Файл `.env` уже настроен с вашими ключами:

```env
BOT_TOKEN=8697819602:AAEithD_psKFXZZZQ4HknXds0y6PGR7UpYc
WEATHER_API_KEY=70e98cc333cd3f3f1e850dbfbe5bb686
NEWS_API_KEY=3wBdqAKzOog6uiylXztpEt6Ef7UkIvyxnejdnEBEYHDdr9pA
```

### Как получить свои ключи (если нужно)

**Telegram Bot Token:**
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в `.env`

**OpenWeatherMap API:**
1. Зарегистрируйтесь на https://openweathermap.org/
2. API Keys → Create Key
3. Скопируйте ключ в `.env`

**NewsAPI:**
1. Зарегистрируйтесь на https://currentsapi.services/
2. Get Your API Key
3. Скопируйте ключ в `.env`

## 🛠 Технологии

- **Python 3.10+**
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy + asyncpg** - работа с PostgreSQL
- **Redis** - кэширование и FSM хранилище
- **APScheduler** - планировщик задач для уведомлений
- **Alembic** - миграции базы данных
- **Docker** - контейнеризация

## 📁 Структура проекта

```
bot/
├── app/
│   ├── handlers/          # Обработчики команд
│   │   ├── start.py       # /start, /help, /stats
│   │   ├── weather.py     # /weather, /forecast
│   │   ├── news.py        # /news
│   │   ├── settings.py    # /setcity, /subscribe, /favorites
│   │   └── callbacks.py   # Обработка кнопок
│   ├── keyboards/         # Клавиатуры (inline и reply)
│   ├── middlewares/       # Middleware (БД, throttling)
│   ├── models/            # Модели базы данных
│   ├── states/            # FSM состояния
│   ├── utils/             # Утилиты (API, планировщик)
│   └── config.py          # Конфигурация
├── migrations/            # Миграции Alembic
├── tests/                 # Тесты
├── main.py               # Точка входа (полная версия)
├── test_bot.py           # Тестовый бот (без БД)
├── requirements.txt      # Зависимости
├── docker-compose.yml    # Docker Compose
├── Dockerfile            # Docker образ
└── .env                  # Переменные окружения
```

## 🐳 Docker развертывание

### Запуск

```bash
# Запуск всех сервисов (PostgreSQL, Redis, Bot)
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down

# Перезапуск
docker-compose restart
```

### Полезные команды

```bash
# Просмотр статуса контейнеров
docker-compose ps

# Подключение к контейнеру бота
docker-compose exec bot bash

# Просмотр логов PostgreSQL
docker-compose logs postgres

# Просмотр логов Redis
docker-compose logs redis
```

## 💾 База данных

### Миграции

```bash
# Применить все миграции
alembic upgrade head

# Создать новую миграцию
alembic revision --autogenerate -m "описание"

# Откатить последнюю миграцию
alembic downgrade -1

# Просмотр истории миграций
alembic history
```

### Подключение к БД

```bash
# Локально
psql -h localhost -U postgres -d telegram_bot

# В Docker
docker-compose exec postgres psql -U postgres -d telegram_bot
```

### Структура таблиц

**users** - пользователи бота
- telegram_id, username, first_name, last_name
- language, default_city
- notification_time, is_subscribed
- created_at, updated_at

**favorites** - избранные города
- user_id, city_name

**news_categories** - категории новостей пользователя
- user_id, category

## 🔧 Makefile команды

```bash
# Установка
make install              # Установка зависимостей
make install-dev          # Установка с dev зависимостями

# Запуск
make run                  # Запуск бота
make docker-up            # Запуск через Docker
make docker-down          # Остановка Docker
make docker-logs          # Просмотр логов Docker

# База данных
make migrate              # Применение миграций
make migrate-create       # Создание новой миграции
make psql                 # Подключение к PostgreSQL

# Разработка
make test                 # Запуск тестов
make lint                 # Проверка кода
make clean                # Очистка временных файлов
```

## 🔍 Устранение проблем

### Бот не запускается

**Проблема:** `ModuleNotFoundError: No module named 'aiogram'`

**Решение:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Проблема:** `TelegramUnauthorizedError`

**Решение:** Проверьте токен бота в `.env`

### Проблемы с БД

**Проблема:** `could not connect to server`

**Решение:**
```bash
# Запустите PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Проверьте подключение
psql -h localhost -U postgres
```

**Проблема:** `database "telegram_bot" does not exist`

**Решение:**
```bash
sudo -u postgres psql
CREATE DATABASE telegram_bot;
\q
```

### Проблемы с Redis

**Проблема:** `redis.exceptions.ConnectionError`

**Решение:**
```bash
# Запустите Redis
sudo systemctl start redis       # Linux
brew services start redis        # macOS

# Проверьте подключение
redis-cli ping
# Должен вернуть: PONG
```

### Проблемы с API

**Проблема:** `❌ Город не найден`

**Решение:** Используйте английское название города или транслитерацию

**Проблема:** `HTTP 401 Unauthorized`

**Решение:** Проверьте API ключи в `.env`

**Проблема:** `HTTP 429 Too Many Requests`

**Решение:** Превышен лимит запросов. Подождите или увеличьте время кэширования в `.env`:
```env
WEATHER_CACHE_TTL=600  # 10 минут
NEWS_CACHE_TTL=3600    # 1 час
```

## 📊 Мониторинг

### Просмотр логов

```bash
# Локально
tail -f bot.log

# Systemd
sudo journalctl -u telegram-bot -f

# Docker
docker-compose logs -f bot
```

### Проверка работы

```bash
# Проверка процесса
ps aux | grep python

# Проверка портов
netstat -tulpn | grep -E '5432|6379'

# Проверка памяти
free -h

# Проверка диска
df -h
```

## 🔐 Безопасность

1. **Не коммитьте `.env` в Git** - он уже в `.gitignore`
2. **Используйте сильные пароли** для PostgreSQL
3. **Ограничьте доступ к БД** - только localhost
4. **Добавьте свой ID в ADMIN_IDS** в `.env`:
   ```env
   ADMIN_IDS=123456789,987654321
   ```
5. **Регулярно обновляйте зависимости:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 🚀 Развертывание на сервере

### Создание systemd service

Создайте файл `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Weather & News Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
Environment="PATH=/path/to/bot/venv/bin"
ExecStart=/path/to/bot/venv/bin/python /path/to/bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## 📈 Производительность

### Кэширование

Бот использует Redis для кэширования:
- **Погода:** 5 минут (300 сек)
- **Новости:** 30 минут (1800 сек)

Настройка в `.env`:
```env
WEATHER_CACHE_TTL=300
NEWS_CACHE_TTL=1800
```

### Throttling

Защита от спама - 1 запрос в секунду на пользователя:
```env
THROTTLE_TIME=1
```

### Рекомендуемые ресурсы

**Минимальные:**
- 1 CPU
- 512 MB RAM
- 5 GB SSD

**Рекомендуемые:**
- 2 CPU
- 1 GB RAM
- 10 GB SSD

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# Конкретный файл
pytest tests/test_weather_api.py

# С покрытием кода
pytest --cov=app tests/
```

### Тестовый бот

Для быстрого тестирования без БД:
```bash
python test_bot.py
```

Доступные команды в тестовом боте:
- `/start` - начать работу
- `/test_weather` - проверить API погоды
- `/test_news` - проверить API новостей

## 💡 Советы по использованию

1. **Начните с тестового бота** для проверки API ключей
2. **Установите город по умолчанию** для быстрого доступа
3. **Добавьте часто используемые города в избранное**
4. **Подпишитесь на утреннюю рассылку** для ежедневной сводки
5. **Используйте Docker** для простого развертывания
6. **Добавьте свой ID в ADMIN_IDS** для доступа к статистике

## 🔮 Планируемые функции

- [ ] Inline-режим для быстрого поиска погоды
- [ ] Команда `/broadcast` для админов
- [ ] Полная поддержка английского языка
- [ ] Графики погоды
- [ ] Уведомления о резких изменениях погоды
- [ ] Карты осадков

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте раздел "Устранение проблем" выше
2. Проверьте логи: `tail -f bot.log`
3. Убедитесь, что все сервисы запущены
4. Проверьте API ключи в `.env`

## 📄 Лицензия

MIT License - см. файл LICENSE

## 🎉 Начало работы

```bash
# Самый простой способ - тестовый бот
python test_bot.py

# Или полная версия с Docker
docker-compose up -d

# Или локально
python main.py
```

Найдите вашего бота в Telegram и отправьте `/start`!

Удачи! 🚀
