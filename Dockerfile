FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий для логов и данных БД
RUN mkdir -p /app/logs /app/data

# Делаем стартовый скрипт исполняемым
RUN chmod +x start.sh

# Открытие порта
#EXPOSE 8000

# Команда запуска
CMD ["./start.sh"]
