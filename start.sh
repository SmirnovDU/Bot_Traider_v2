#!/bin/bash

# Получаем порт из переменной окружения или используем 8000 по умолчанию
PORT=${PORT:-8000}

echo "Starting server on port $PORT"

# Запускаем сервер
python -m uvicorn bot.main:app --host 0.0.0.0 --port $PORT
