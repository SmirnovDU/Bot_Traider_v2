# API Документация

## Обзор

Trading Bot API предоставляет RESTful интерфейс для автоматической торговли на основе сигналов от TradingView.

**Base URL**: `https://your-app-name.onrender.com`

## Аутентификация

Все webhook запросы должны содержать секретный ключ в поле `secret`.

```json
{
  "secret": "your_webhook_secret_key"
}
```

## Endpoints

### 1. GET /status

Проверка статуса API.

**Запрос:**
```bash
curl https://your-app-name.onrender.com/status
```

**Ответ:**
```json
{
  "status": "ok"
}
```

**Коды ответа:**
- `200` - API работает нормально
- `500` - Внутренняя ошибка сервера

---

### 2. GET /balances

Получение текущих балансов на всех биржах.

**Запрос:**
```bash
curl https://your-app-name.onrender.com/balances
```

**Ответ:**
```json
{
  "balances": [
    ["Bybit", "USDT", 1000.0],
    ["Binance", "USDT", 1000.0],
    ["Bybit", "BTC", 0.05],
    ["Binance", "ETH", 2.5]
  ]
}
```

**Формат ответа:**
- `[exchange, coin, amount]` - массив с биржей, валютой и количеством

---

### 3. POST /webhook

Основной endpoint для получения торговых сигналов от TradingView.

#### Покупка (Buy)

**Запрос:**
```bash
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "action": "buy",
    "symbol": "BTCUSDT",
    "usdt_amount": 100
  }'
```

**Параметры:**
- `secret` (string, обязательный) - секретный ключ для аутентификации
- `action` (string, обязательный) - должно быть "buy"
- `symbol` (string, обязательный) - торговая пара (например, "BTCUSDT")
- `usdt_amount` (number, обязательный) - сумма в USDT для покупки

**Успешный ответ:**
```json
{
  "status": "ok",
  "request_id": "20250815_123456_BTCUSDT_BUY",
  "exchange": "Bybit",
  "order": {
    "status": "filled",
    "side": "buy",
    "symbol": "BTCUSDT",
    "qty": 0.002,
    "price": 50000.0,
    "fee": 0.05
  },
  "balance_after": 900.0,
  "profit": null
}
```

#### Продажа (Sell)

**Запрос:**
```bash
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "action": "sell",
    "symbol": "BTCUSDT"
  }'
```

**Параметры:**
- `secret` (string, обязательный) - секретный ключ для аутентификации
- `action` (string, обязательный) - должно быть "sell"
- `symbol` (string, обязательный) - торговая пара
- `exchange` (string, опциональный) - биржа для продажи (по умолчанию используется DEFAULT_EXCHANGE)

**Успешный ответ:**
```json
{
  "status": "ok",
  "request_id": "20250815_123457_BTCUSDT_SELL",
  "exchange": "Bybit",
  "order": {
    "status": "filled",
    "side": "sell",
    "symbol": "BTCUSDT",
    "qty": 0.002,
    "price": 51000.0,
    "fee": 0.051
  },
  "balance_after": 1019.95,
  "profit": 19.95
}
```

## Коды ошибок

### 400 Bad Request
```json
{
  "detail": "Invalid action"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message"
}
```

### Ошибки торговли
```json
{
  "status": "Error",
  "reason": "Amount exceeds 10% of balance",
  "balance": 1000.0,
  "max_amount": 100.0
}
```

## Логика работы

### Выбор биржи для покупки

1. **Получение цен** с обеих бирж (Bybit и Binance)
2. **Проверка балансов** на обеих биржах
3. **Выбор биржи с лучшей ценой**
4. **Проверка достаточности средств**
5. **Fallback на вторую биржу** при необходимости

### Ограничения

- **Максимальный размер позиции**: 10% от баланса USDT
- **Минимальная сумма**: зависит от биржи
- **Поддерживаемые пары**: все пары с USDT

### Расчёт комиссий

- **Для покупки**: `стоимость монет в сделке - баланс монет после сделки * цена`
- **Для продажи**: `средства на счете перед сделкой + стоимость сделки - баланс после сделки`

## Примеры использования

### TradingView Alert

#### Pine Script
```pinescript
//@version=5
indicator("Trading Bot Signal")

rsi = ta.rsi(close, 14)
buy_signal = rsi < 30
sell_signal = rsi > 70

alertcondition(buy_signal, title="Buy Signal", message='{"secret":"your_secret","action":"buy","symbol":"{{ticker}}","usdt_amount":"100"}')
alertcondition(sell_signal, title="Sell Signal", message='{"secret":"your_secret","action":"sell","symbol":"{{ticker}}"}')
```

#### Настройка Alert
1. Создайте Alert на основе индикатора
2. Выберите "Webhook URL"
3. Введите: `https://your-app-name.onrender.com/webhook`
4. Настройте сообщение как показано выше

### Тестирование с curl

```bash
# Проверка статуса
curl https://your-app-name.onrender.com/status

# Проверка балансов
curl https://your-app-name.onrender.com/balances

# Тестовая покупка
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_secret",
    "action": "buy",
    "symbol": "BTCUSDT",
    "usdt_amount": 50
  }'

# Тестовая продажа
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_secret",
    "action": "sell",
    "symbol": "BTCUSDT"
  }'
```

## Мониторинг

### Логи

Все операции логируются с помощью `loguru`:

```
2025-08-15 12:34:56.789 | INFO | webhook:webhook:16 - Сигнал: {'secret': '***', 'action': 'buy', 'symbol': 'BTCUSDT', 'usdt_amount': 100}
2025-08-15 12:34:56.790 | INFO | exchange_selector:get_best_price_exchange:25 - Цены BTCUSDT: Bybit=50000.0, Binance=50001.0
2025-08-15 12:34:56.791 | INFO | exchange_selector:get_best_price_exchange:32 - Балансы из БД: Bybit=1000.0, Binance=1000.0
2025-08-15 12:34:56.792 | INFO | exchange_selector:get_best_price_exchange:53 - Выбрана биржа Bybit (лучшая цена: 50000.0, средства: есть)
2025-08-15 12:34:56.793 | INFO | webhook:webhook:32 - Выбрана биржа Bybit для покупки по цене 50000.0
2025-08-15 12:34:56.794 | INFO | exchanges.bybit:place_order:84 - [TEST] Ордер buy 0.002 BTCUSDT по цене 50000.0, комиссия: 0.05
2025-08-15 12:34:56.795 | INFO | db:save_trade:98 - Сделка сохранена: 20250815_123456_BTCUSDT_BUY
2025-08-15 12:34:56.796 | INFO | webhook:webhook:100 - Сделка выполнена: 20250815_123456_BTCUSDT_BUY - buy 0.002 BTCUSDT по 50000.0
```

### Метрики

Ключевые метрики для мониторинга:

- **Количество сделок** в единицу времени
- **Процент успешных сделок**
- **Средняя прибыль** на сделку
- **Время отклика** API
- **Ошибки** и их типы

## Безопасность

### Рекомендации

1. **Используйте сложный секретный ключ** (минимум 32 символа)
2. **Ограничьте доступ** к API по IP адресам (если возможно)
3. **Мониторьте логи** на подозрительную активность
4. **Регулярно обновляйте** секретные ключи
5. **Используйте HTTPS** для всех запросов

### Ограничения API ключей

Настройте API ключи бирж с минимальными правами:

- **Bybit**: Spot Trading, Read-only для балансов
- **Binance**: Spot Trading, Read-only для балансов

---

**Для дополнительной поддержки создайте Issue на GitHub.**
