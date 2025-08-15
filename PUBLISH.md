# 🚀 Руководство по публикации

## Шаг 1: Подготовка к публикации

### 1.1 Проверка файлов

Убедитесь, что у вас есть все необходимые файлы:

```bash
ls -la
```

Должны быть следующие файлы:
- ✅ `README.md` - документация
- ✅ `requirements.txt` - зависимости
- ✅ `render.yaml` - конфигурация Render
- ✅ `Dockerfile` - Docker образ
- ✅ `.dockerignore` - исключения для Docker
- ✅ `.gitignore` - исключения для Git
- ✅ `LICENSE` - лицензия
- ✅ `DEPLOYMENT.md` - руководство по развёртыванию
- ✅ `docs/API.md` - документация API
- ✅ `.github/workflows/deploy.yml` - CI/CD
- ✅ `bot/` - основной код
- ✅ `test_*.py` - тесты

### 1.2 Финальная проверка

Запустите все тесты:

```bash
python3 test_bot.py
python3 test_webhook.py
python3 test_exchange_selector.py
python3 test_balance_scenario.py
python3 test_balance_source.py
python3 test_webhook_fix.py
python3 demo_v3.py
```

## Шаг 2: Создание GitHub репозитория

### 2.1 Инициализация Git

```bash
# Инициализируйте Git репозиторий
git init

# Добавьте все файлы
git add .

# Создайте первый коммит
git commit -m "Initial commit: Trading Bot v3.0"

# Добавьте remote (замените на ваш URL)
git remote add origin https://github.com/your-username/trading-bot.git

# Отправьте в GitHub
git push -u origin main
```

### 2.2 Настройка GitHub

1. **Перейдите на GitHub** и создайте новый репозиторий
2. **Назовите его** `trading-bot`
3. **Сделайте публичным** (или приватным по желанию)
4. **Не инициализируйте** с README (у нас уже есть)

## Шаг 3: Настройка GitHub Pages (опционально)

### 3.1 Создание документации

```bash
# Создайте папку docs для GitHub Pages
mkdir -p docs
cp README.md docs/index.md
cp docs/API.md docs/api.md
cp DEPLOYMENT.md docs/deployment.md
```

### 3.2 Настройка в GitHub

1. **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main
4. **Folder**: /docs

## Шаг 4: Развёртывание на Render.com

### 4.1 Создание аккаунта

1. **Зарегистрируйтесь** на [Render.com](https://render.com)
2. **Подключите GitHub** аккаунт

### 4.2 Создание Web Service

1. **New** → **Web Service**
2. **Connect** ваш GitHub репозиторий
3. **Выберите** `trading-bot` репозиторий

### 4.3 Настройка сервиса

#### Основные настройки:
- **Name**: `trading-bot`
- **Environment**: `Python 3`
- **Region**: Выберите ближайший
- **Branch**: `main`

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
python -m uvicorn bot.main:app --host 0.0.0.0 --port $PORT
```

### 4.4 Переменные окружения

Добавьте в **Environment Variables**:

```env
TEST_MODE=True
WEBHOOK_SECRET=your_very_secure_secret_key_here
DEFAULT_EXCHANGE=bybit
TEST_BALANCE_USDT=1000
```

### 4.5 Deploy

1. **Нажмите "Create Web Service"**
2. **Дождитесь** завершения сборки (2-3 минуты)
3. **Скопируйте URL** вашего сервиса

## Шаг 5: Настройка TradingView

### 5.1 Создание Pine Script

Создайте индикатор в TradingView:

```pinescript
//@version=5
indicator("Trading Bot Signal", overlay=true)

// Простая торговая логика
rsi = ta.rsi(close, 14)
oversold = rsi < 30
overbought = rsi > 70

// Сигналы
buy_signal = oversold and close > close[1]
sell_signal = overbought and close < close[1]

// Отображение
plotshape(buy_signal, title="Buy", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)
plotshape(sell_signal, title="Sell", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)

// Экспорт для webhook
export buy_signal
export sell_signal
```

### 5.2 Настройка Alert

1. **Создайте Alert** на основе индикатора
2. **Условие**: `buy_signal` или `sell_signal`
3. **Действие**: Webhook URL
4. **URL**: `https://your-app-name.onrender.com/webhook`

#### Сообщение для покупки:
```json
{
  "secret": "your_webhook_secret",
  "action": "buy",
  "symbol": "{{ticker}}",
  "usdt_amount": "100"
}
```

#### Сообщение для продажи:
```json
{
  "secret": "your_webhook_secret",
  "action": "sell",
  "symbol": "{{ticker}}"
}
```

## Шаг 6: Тестирование

### 6.1 Проверка API

```bash
# Проверка статуса
curl https://your-app-name.onrender.com/status

# Проверка балансов
curl https://your-app-name.onrender.com/balances

# Тестовый webhook
curl -X POST https://your-app-name.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "action": "buy",
    "symbol": "BTCUSDT",
    "usdt_amount": 10
  }'
```

### 6.2 Мониторинг логов

1. **Откройте** ваш сервис в Render Dashboard
2. **Перейдите** на вкладку "Logs"
3. **Мониторьте** в реальном времени

## Шаг 7: Переход в боевой режим

### 7.1 Подготовка API ключей

1. **Создайте API ключи** на Bybit и Binance
2. **Ограничьте права** только на Spot Trading
3. **Сохраните** ключи в безопасном месте

### 7.2 Обновление переменных окружения

В Render Dashboard обновите переменные:

```env
TEST_MODE=False
WEBHOOK_SECRET=your_very_secure_secret_key_here
DEFAULT_EXCHANGE=bybit
API_KEY_BYBIT=your_bybit_api_key
API_SECRET_BYBIT=your_bybit_secret
API_KEY_BINANCE=your_binance_api_key
API_SECRET_BINANCE=your_binance_secret
```

### 7.3 Перезапуск сервиса

1. **Redeploy** сервис в Render
2. **Проверьте** логи на ошибки
3. **Протестируйте** с небольшими суммами

## Шаг 8: Мониторинг и поддержка

### 8.1 Настройка мониторинга

1. **Uptime Robot** - мониторинг доступности
2. **Render Logs** - мониторинг логов
3. **GitHub Issues** - отслеживание проблем

### 8.2 Обновления

```bash
# Получите обновления
git pull origin main

# Протестируйте локально
python3 test_*.py

# Отправьте в GitHub
git add .
git commit -m "Update: description"
git push origin main

# Render автоматически обновится
```

## 🎉 Готово!

Ваш торговый бот успешно развёрнут и готов к использованию!

### Полезные ссылки:

- **GitHub**: https://github.com/your-username/trading-bot
- **Render**: https://dashboard.render.com/web/your-app-name
- **API**: https://your-app-name.onrender.com/status
- **Документация**: https://your-username.github.io/trading-bot

### Поддержка:

- **Issues**: https://github.com/your-username/trading-bot/issues
- **Discussions**: https://github.com/your-username/trading-bot/discussions
- **Wiki**: https://github.com/your-username/trading-bot/wiki

---

**Удачной торговли! 🚀**
