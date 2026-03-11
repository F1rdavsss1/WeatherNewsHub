#!/bin/bash

echo "🚀 Запуск WeatherNews Hub Frontend..."

# Проверка наличия node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Установка зависимостей..."
    npm install
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚙️  Создание .env файла..."
    cp .env.example .env
    echo "✅ .env файл создан. Отредактируйте его при необходимости."
fi

echo "🌐 Запуск dev сервера..."
npm run dev
