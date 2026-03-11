.PHONY: help install run docker-up docker-down docker-logs migrate test lint clean

help:
	@echo "Доступные команды:"
	@echo "  make install      - Установка зависимостей"
	@echo "  make run          - Запуск бота локально"
	@echo "  make docker-up    - Запуск через Docker Compose"
	@echo "  make docker-down  - Остановка Docker контейнеров"
	@echo "  make docker-logs  - Просмотр логов Docker"
	@echo "  make migrate      - Применение миграций БД"
	@echo "  make test         - Запуск тестов"
	@echo "  make lint         - Проверка кода"
	@echo "  make clean        - Очистка временных файлов"

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python main.py

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bot

docker-rebuild:
	docker-compose up -d --build

migrate:
	. venv/bin/activate && alembic upgrade head

migrate-create:
	. venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

test:
	. venv/bin/activate && pytest tests/ -v

lint:
	. venv/bin/activate && flake8 app/ --max-line-length=120

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
