# 🗄️ Деплой с постоянной базой данных

## Проблема
При каждом деплое на Railway/Render/других платформах база данных SQLite пересоздавалась, теряя все данные о покупках и сделках.

## Решение

### 1. 🐳 Docker Compose (Локально)

```bash
# Создать .env файл с переменными
cp env.example .env

# Запустить с постоянным volume
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f trading-bot

# Остановить
docker-compose down

# Остановить с удалением volume (ОСТОРОЖНО - потеря данных!)
docker-compose down -v
```

### 2. ☁️ Railway.app (Рекомендуется)

#### Вариант A: Railway Volume (если поддерживается)
```bash
# В railway.toml добавить:
[build]
  buildCommand = "pip install -r requirements.txt"

[deploy]
  startCommand = "./start.sh"

[env]
  DB_PATH = "/data/trades.db"

# Создать volume через Railway Dashboard
```

#### Вариант B: Railway PostgreSQL
1. Добавить PostgreSQL addon в Railway
2. Изменить `bot/db.py` для работы с PostgreSQL
3. Обновить `requirements.txt`: добавить `psycopg2-binary`

### 3. 🌐 Render.com

#### Вариант A: Render Disk
```yaml
# render.yaml
services:
  - type: web
    name: trading-bot
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "./start.sh"
    disk:
      name: trading-bot-data
      mountPath: /app/data
      sizeGB: 1
    envVars:
      - key: DB_PATH
        value: /app/data/trades.db
```

#### Вариант B: Render PostgreSQL
1. Создать PostgreSQL database в Render
2. Изменить код для работы с PostgreSQL

### 4. 🏠 VPS/Собственный сервер

```bash
# Клонировать репозиторий
git clone https://github.com/ваш-пользователь/Bot_Traider.git
cd Bot_Traider

# Создать .env
cp env.example .env
# Отредактировать .env с вашими настройками

# Запустить через Docker Compose
docker-compose up -d

# Или через systemd service
sudo cp deploy/trading-bot.service /etc/systemd/system/
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

## 🔧 Переменные окружения

### Новые переменные для постоянной БД:
```bash
# Путь к файлу БД (для Docker volume)
DB_PATH=/app/data/trades.db

# Для PostgreSQL (альтернатива)
DATABASE_URL=postgresql://user:password@host:port/dbname
USE_POSTGRESQL=true
```

## 📊 Проверка работы

### Тест сохранения данных:
```bash
# Сделать покупку
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"secret":"your_secret","action":"buy","symbol":"BTCUSDT","usdt_amount":10}'

# Проверить балансы
curl http://localhost:8000/balances

# Перезапустить контейнер
docker-compose restart

# Проверить что данные сохранились
curl http://localhost:8000/balances
```

### Telegram команды:
- `/balances` - проверить балансы
- `/status` - статус бота
- `/profit` - статистика прибыли

## 🚨 Важные моменты

### ✅ Правильно:
- Использовать внешние volume для БД
- Регулярно делать бэкапы БД
- Мониторить размер БД

### ❌ Неправильно:
- Хранить БД внутри контейнера
- Не делать бэкапы
- Игнорировать логи ошибок

## 🔄 Миграция существующих данных

Если у вас уже есть данные в старой БД:

```bash
# Скопировать БД из контейнера
docker cp container_name:/app/bot/trades.db ./backup_trades.db

# Поместить в новый volume
docker cp ./backup_trades.db container_name:/app/data/trades.db

# Или через bind mount
cp ./backup_trades.db /path/to/docker/volume/trades.db
```

## 📈 Мониторинг

### Полезные команды:
```bash
# Размер БД
docker exec container_name ls -lh /app/data/trades.db

# Количество сделок
docker exec container_name sqlite3 /app/data/trades.db "SELECT COUNT(*) FROM trades"

# Последние сделки
docker exec container_name sqlite3 /app/data/trades.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5"
```

## 🎯 Результат

После правильного деплоя:
- ✅ БД сохраняется между перезапусками
- ✅ Данные о покупках не теряются
- ✅ История сделок полная
- ✅ Балансы актуальные
- ✅ Статистика прибыли правильная
