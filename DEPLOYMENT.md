# Руководство по развёртыванию

## 🚀 Развёртывание на Render.com

### Шаг 1: Подготовка GitHub репозитория

1. **Fork репозитория** на GitHub
2. **Клонируйте** ваш fork локально:
```bash
git clone https://github.com/your-username/trading-bot.git
cd trading-bot
```

3. **Проверьте структуру проекта**:
```
trading-bot/
├── bot/
│   ├── main.py
│   ├── webhook.py
│   ├── config.py
│   ├── db.py
│   ├── utils.py
│   ├── exchange_selector.py
│   └── exchanges/
│       ├── bybit.py
│       └── binance.py
├── requirements.txt
├── render.yaml
├── Dockerfile
├── README.md
└── .env.example
```

### Шаг 2: Настройка Render.com

1. **Зарегистрируйтесь** на [Render.com](https://render.com)
2. **Создайте новый Web Service**
3. **Подключите GitHub репозиторий**
4. **Выберите ветку** (обычно `main`)

### Шаг 3: Конфигурация сервиса

#### Основные настройки:
- **Name**: `trading-bot`
- **Environment**: `Python 3`
- **Region**: Выберите ближайший к вам
- **Branch**: `main`
- **Root Directory**: оставьте пустым

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
python -m uvicorn bot.main:app --host 0.0.0.0 --port $PORT
```

### Шаг 4: Переменные окружения

Добавьте следующие переменные в Render Dashboard:

#### Обязательные:
```env
TEST_MODE=True
WEBHOOK_SECRET=your_very_secure_secret_key_here
DEFAULT_EXCHANGE=bybit
TEST_BALANCE_USDT=1000
```

#### Для боевого режима (TEST_MODE=False):
```env
API_KEY_BYBIT=your_bybit_api_key
API_SECRET_BYBIT=your_bybit_secret
API_KEY_BINANCE=your_binance_api_key
API_SECRET_BINANCE=your_binance_secret
```

### Шаг 5: Deploy

1. **Нажмите "Create Web Service"**
2. **Дождитесь завершения сборки** (обычно 2-3 минуты)
3. **Проверьте логи** на предмет ошибок

### Шаг 6: Проверка работоспособности

После успешного деплоя проверьте:

1. **Статус API**:
```bash
curl https://your-app-name.onrender.com/status
```

2. **Балансы**:
```bash
curl https://your-app-name.onrender.com/balances
```

3. **Webhook** (тестовый запрос):
```bash
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "action": "buy",
    "symbol": "BTCUSDT",
    "usdt_amount": 10
  }'
```

## 🐳 Развёртывание с Docker

### Локальный Docker

1. **Соберите образ**:
```bash
docker build -t trading-bot .
```

2. **Запустите контейнер**:
```bash
docker run -p 8000:8000 --env-file .env trading-bot
```

### Docker на Render.com

1. **Используйте существующий Dockerfile**
2. **Настройте переменные окружения** как описано выше
3. **Render автоматически использует Dockerfile**

## 🔧 Настройка TradingView

### 1. Создание Pine Script

Создайте индикатор в TradingView:

```pinescript
//@version=5
indicator("Trading Bot Signal", overlay=true)

// Ваша торговая логика
rsi = ta.rsi(close, 14)
oversold = rsi < 30
overbought = rsi > 70

// Сигналы
buy_signal = oversold and close > close[1]
sell_signal = overbought and close < close[1]

// Отображение сигналов
plotshape(buy_signal, title="Buy", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)
plotshape(sell_signal, title="Sell", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)

// Экспорт переменных для webhook
export buy_signal
export sell_signal
```

### 2. Настройка Alert

1. **Создайте Alert** на основе вашего индикатора
2. **Настройте условия** (например, `buy_signal` или `sell_signal`)
3. **Выберите "Webhook URL"**
4. **Введите URL вашего бота**:
```
https://your-app-name.onrender.com/webhook
```

### 3. Настройка сообщения

#### Для покупки:
```json
{
  "secret": "your_webhook_secret",
  "action": "buy",
  "symbol": "{{ticker}}",
  "usdt_amount": "100"
}
```

#### Для продажи:
```json
{
  "secret": "your_webhook_secret",
  "action": "sell",
  "symbol": "{{ticker}}"
}
```

## 🔍 Мониторинг и логи

### Просмотр логов на Render.com

1. **Откройте ваш сервис** в Render Dashboard
2. **Перейдите на вкладку "Logs"**
3. **Мониторьте в реальном времени**

### Ключевые события для мониторинга:

- ✅ **Успешные сделки**: `Сделка выполнена`
- ⚠️ **Ошибки**: `Ошибка выполнения сделки`
- 🔍 **Выбор биржи**: `Выбрана биржа`
- 💰 **Fallback**: `Bybit недостаточно средств`

## 🛠️ Устранение неполадок

### Частые проблемы:

#### 1. "Module not found"
- **Решение**: Проверьте `requirements.txt` и пересоберите

#### 2. "Port already in use"
- **Решение**: Используйте `$PORT` в команде запуска

#### 3. "Database locked"
- **Решение**: SQLite может иметь проблемы в production. Рассмотрите PostgreSQL

#### 4. "Webhook timeout"
- **Решение**: Увеличьте timeout в TradingView или оптимизируйте код

### Проверка работоспособности:

```bash
# Проверка статуса
curl https://your-app-name.onrender.com/status

# Проверка балансов
curl https://your-app-name.onrender.com/balances

# Тестовый webhook
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"secret":"test","action":"buy","symbol":"BTCUSDT","usdt_amount":10}'
```

## 🔒 Безопасность

### Рекомендации:

1. **Используйте сложный WEBHOOK_SECRET**
2. **Не коммитьте .env файлы**
3. **Ограничьте API ключи** только необходимыми правами
4. **Мониторьте логи** на подозрительную активность
5. **Регулярно обновляйте зависимости**

### Переменные окружения:

```env
# Минимальные права для API ключей
# Bybit: Spot Trading, Read-only для балансов
# Binance: Spot Trading, Read-only для балансов
```

## 📈 Масштабирование

### Для высоких нагрузок:

1. **Обновите план** на Render.com (Pro)
2. **Добавьте кэширование** (Redis)
3. **Используйте PostgreSQL** вместо SQLite
4. **Добавьте мониторинг** (Uptime Robot)
5. **Настройте алерты** на email/SMS

---

**Удачного развёртывания! 🚀**

# Руководство по развёртыванию

## 🚀 Развёртывание на Render.com

### Шаг 1: Подготовка GitHub репозитория

1. **Fork репозитория** на GitHub
2. **Клонируйте** ваш fork локально:
```bash
git clone https://github.com/your-username/trading-bot.git
cd trading-bot
```

3. **Проверьте структуру проекта**:
```
trading-bot/
├── bot/
│   ├── main.py
│   ├── webhook.py
│   ├── config.py
│   ├── db.py
│   ├── utils.py
│   ├── exchange_selector.py
│   └── exchanges/
│       ├── bybit.py
│       └── binance.py
├── requirements.txt
├── render.yaml
├── Dockerfile
├── README.md
└── .env.example
```

### Шаг 2: Настройка Render.com

1. **Зарегистрируйтесь** на [Render.com](https://render.com)
2. **Создайте новый Web Service**
3. **Подключите GitHub репозиторий**
4. **Выберите ветку** (обычно `main`)

### Шаг 3: Конфигурация сервиса

#### Основные настройки:
- **Name**: `trading-bot`
- **Environment**: `Python 3`
- **Region**: Выберите ближайший к вам
- **Branch**: `main`
- **Root Directory**: оставьте пустым

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
python -m uvicorn bot.main:app --host 0.0.0.0 --port $PORT
```

### Шаг 4: Переменные окружения

Добавьте следующие переменные в Render Dashboard:

#### Обязательные:
```env
TEST_MODE=True
WEBHOOK_SECRET=your_very_secure_secret_key_here
DEFAULT_EXCHANGE=bybit
TEST_BALANCE_USDT=1000
```

#### Для боевого режима (TEST_MODE=False):
```env
API_KEY_BYBIT=your_bybit_api_key
API_SECRET_BYBIT=your_bybit_secret
API_KEY_BINANCE=your_binance_api_key
API_SECRET_BINANCE=your_binance_secret
```

### Шаг 5: Deploy

1. **Нажмите "Create Web Service"**
2. **Дождитесь завершения сборки** (обычно 2-3 минуты)
3. **Проверьте логи** на предмет ошибок

### Шаг 6: Проверка работоспособности

После успешного деплоя проверьте:

1. **Статус API**:
```bash
curl https://your-app-name.onrender.com/status
```

2. **Балансы**:
```bash
curl https://your-app-name.onrender.com/balances
```

3. **Webhook** (тестовый запрос):
```bash
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "action": "buy",
    "symbol": "BTCUSDT",
    "usdt_amount": 10
  }'
```

## 🐳 Развёртывание с Docker

### Локальный Docker

1. **Соберите образ**:
```bash
docker build -t trading-bot .
```

2. **Запустите контейнер**:
```bash
docker run -p 8000:8000 --env-file .env trading-bot
```

### Docker на Render.com

1. **Используйте существующий Dockerfile**
2. **Настройте переменные окружения** как описано выше
3. **Render автоматически использует Dockerfile**

## 🔧 Настройка TradingView

### 1. Создание Pine Script

Создайте индикатор в TradingView:

```pinescript
//@version=5
indicator("Trading Bot Signal", overlay=true)

// Ваша торговая логика
rsi = ta.rsi(close, 14)
oversold = rsi < 30
overbought = rsi > 70

// Сигналы
buy_signal = oversold and close > close[1]
sell_signal = overbought and close < close[1]

// Отображение сигналов
plotshape(buy_signal, title="Buy", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)
plotshape(sell_signal, title="Sell", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)

// Экспорт переменных для webhook
export buy_signal
export sell_signal
```

### 2. Настройка Alert

1. **Создайте Alert** на основе вашего индикатора
2. **Настройте условия** (например, `buy_signal` или `sell_signal`)
3. **Выберите "Webhook URL"**
4. **Введите URL вашего бота**:
```
https://your-app-name.onrender.com/webhook
```

### 3. Настройка сообщения

#### Для покупки:
```json
{
  "secret": "your_webhook_secret",
  "action": "buy",
  "symbol": "{{ticker}}",
  "usdt_amount": "100"
}
```

#### Для продажи:
```json
{
  "secret": "your_webhook_secret",
  "action": "sell",
  "symbol": "{{ticker}}"
}
```

## 🔍 Мониторинг и логи

### Просмотр логов на Render.com

1. **Откройте ваш сервис** в Render Dashboard
2. **Перейдите на вкладку "Logs"**
3. **Мониторьте в реальном времени**

### Ключевые события для мониторинга:

- ✅ **Успешные сделки**: `Сделка выполнена`
- ⚠️ **Ошибки**: `Ошибка выполнения сделки`
- 🔍 **Выбор биржи**: `Выбрана биржа`
- 💰 **Fallback**: `Bybit недостаточно средств`

## 🛠️ Устранение неполадок

### Частые проблемы:

#### 1. "Module not found"
- **Решение**: Проверьте `requirements.txt` и пересоберите

#### 2. "Port already in use"
- **Решение**: Используйте `$PORT` в команде запуска

#### 3. "Database locked"
- **Решение**: SQLite может иметь проблемы в production. Рассмотрите PostgreSQL

#### 4. "Webhook timeout"
- **Решение**: Увеличьте timeout в TradingView или оптимизируйте код

### Проверка работоспособности:

```bash
# Проверка статуса
curl https://your-app.onrender.com/status

# Проверка балансов
curl https://your-app.onrender.com/balances

# Тестовый webhook
curl -X POST https://your-app.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"secret":"test","action":"buy","symbol":"BTCUSDT","usdt_amount":10}'
```

## 🔒 Безопасность

### Рекомендации:

1. **Используйте сложный WEBHOOK_SECRET**
2. **Не коммитьте .env файлы**
3. **Ограничьте API ключи** только необходимыми правами
4. **Мониторьте логи** на подозрительную активность
5. **Регулярно обновляйте зависимости**

### Переменные окружения:

```env
# Минимальные права для API ключей
# Bybit: Spot Trading, Read-only для балансов
# Binance: Spot Trading, Read-only для балансов
```

## 📈 Масштабирование

### Для высоких нагрузок:

1. **Обновите план** на Render.com (Pro)
2. **Добавьте кэширование** (Redis)
3. **Используйте PostgreSQL** вместо SQLite
4. **Добавьте мониторинг** (Uptime Robot)
5. **Настройте алерты** на email/SMS

---

**Удачного развёртывания! 🚀**
