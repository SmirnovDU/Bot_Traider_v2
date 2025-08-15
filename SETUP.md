# Инструкция по настройке и запуску торгового бота

## Быстрый старт

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Создание конфигурации
Создайте файл `.env` в папке `bot/` на основе `env.example`:

```bash
cp env.example bot/.env
```

Отредактируйте `.env` файл:
```env
# API ключи Bybit
API_KEY_BYBIT=your_bybit_api_key_here
API_SECRET_BYBIT=your_bybit_secret_here

# API ключи Binance
API_KEY_BINANCE=your_binance_api_key_here
API_SECRET_BINANCE=your_binance_secret_here

# Секрет для webhook
WEBHOOK_SECRET=your_secure_secret_here

# Настройки режима работы
TEST_MODE=True
DEFAULT_EXCHANGE=bybit

# Тестовые балансы (используются только в TEST_MODE)
TEST_BALANCE_USDT=100
```

### 3. Запуск бота
```bash
cd bot
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Тестирование
```bash
# Тест основных функций
python3 test_bot.py

# Тест webhook API
python3 test_webhook.py

# Детальный тест
python3 test_detailed.py
```

## Настройка TradingView

### 1. Создание алерта в TradingView
В вашем индикаторе TradingView добавьте алерт с JSON сообщением:

```json
{
  "secret": "your_webhook_secret",
  "action": "buy",
  "symbol": "{{ticker}}",
  "usdt_amount": 10,
  "exchange": "bybit"
}
```

### 2. Настройка webhook URL
В настройках алерта укажите:
- **URL**: `http://your-server:8000/webhook`
- **Method**: POST
- **Content-Type**: application/json

## API Endpoints

### GET /
Статус бота
```json
{"status": "ok"}
```

### GET /balances
Текущие балансы
```json
{
  "balances": [
    ["Bybit", "USDT", 89.99],
    ["Binance", "USDT", 100.0],
    ["Bybit", "BTC", 0.1]
  ]
}
```

### POST /webhook
Обработка сигналов TradingView

**Параметры:**
- `secret` - секретный ключ
- `action` - "buy" или "sell"
- `symbol` - торговая пара (например, "BTCUSDT")
- `usdt_amount` - сумма в USDT (только для покупки)
- `exchange` - биржа (опционально, по умолчанию DEFAULT_EXCHANGE)

**Пример запроса:**
```json
{
  "secret": "your_webhook_secret",
  "action": "buy",
  "symbol": "BTCUSDT",
  "usdt_amount": 10,
  "exchange": "bybit"
}
```

**Ответ:**
```json
{
  "status": "ok",
  "request_id": "20250814_233731_BTCUSDT_BUY",
  "order": {...},
  "balance_after": 89.99,
  "profit": null
}
```

## Режимы работы

### Тестовый режим (TEST_MODE=True)
- Использует тестовые балансы из .env
- Эмулирует сделки без отправки на биржу
- Записывает результаты в БД
- Идеально для тестирования стратегий

### Боевой режим (TEST_MODE=False)
- Отправляет реальные ордера на биржи
- Получает актуальные балансы с бирж
- Использует реальные комиссии
- **ВНИМАНИЕ**: Используйте только после тщательного тестирования!

## База данных

Бот использует SQLite базу данных `bot/trades.db` с двумя таблицами:

### trades
История всех сделок:
- `id` - уникальный идентификатор
- `request_id` - уникальный ID запроса (формат: YYYYMMDD_HHMMSS_SYMBOL_SIDE)
- `timestamp` - время сделки
- `exchange` - биржа
- `side` - сторона сделки (buy/sell)
- `symbol` - торговая пара
- `price` - цена исполнения
- `qty` - количество
- `amount_usdt` - сумма в USDT
- `fee` - комиссия
- `profit` - прибыль (для продаж)
- `balance_after` - баланс после сделки
- `note` - дополнительные заметки

### balances
Текущие балансы:
- `exchange` - биржа
- `coin` - валюта
- `amount` - количество

## Безопасность

1. **API ключи**: Храните в .env файле, не коммитьте в git
2. **Webhook секрет**: Используйте сложный секретный ключ
3. **Ограничения**: Бот ограничивает позиции 10% от баланса
4. **Логирование**: Все операции логируются в bot.log

## Мониторинг

### Логи
Логи сохраняются в `bot.log` с ротацией:
- Максимальный размер файла: 10 МБ
- Хранение: 7 дней
- Сжатие: ZIP

### База данных
```bash
# Просмотр сделок
sqlite3 bot/trades.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;"

# Просмотр балансов
sqlite3 bot/trades.db "SELECT * FROM balances;"

# Статистика
sqlite3 bot/trades.db "SELECT COUNT(*) as total_trades, SUM(profit) as total_profit FROM trades WHERE profit IS NOT NULL;"
```

## Устранение неполадок

### Бот не запускается
1. Проверьте установку зависимостей: `pip3 install -r requirements.txt`
2. Проверьте .env файл
3. Проверьте логи: `tail -f bot.log`

### Webhook не работает
1. Проверьте секретный ключ
2. Проверьте формат JSON
3. Проверьте доступность сервера

### Ошибки API
1. Проверьте API ключи
2. Проверьте права доступа на бирже
3. Проверьте лимиты API

## Поддержка

При возникновении проблем:
1. Проверьте логи в `bot.log`
2. Запустите тесты: `python3 test_bot.py`
3. Проверьте базу данных
4. Убедитесь в корректности конфигурации
