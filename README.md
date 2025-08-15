# Trading Bot для TradingView

🤖 Автоматический торговый бот для работы с сигналами TradingView, поддерживающий Bybit и Binance с умным выбором биржи.

## ✨ Возможности

- 🔄 **Автоматическая торговля** по сигналам TradingView
- 🏦 **Поддержка двух бирж**: Bybit и Binance
- 🧠 **Умный выбор биржи** по лучшей цене и достаточности средств
- 💰 **Fallback механизм** - автоматический переход на вторую биржу
- 📊 **SQLite база данных** для хранения сделок и балансов
- 🛡️ **Ограничение позиций** (10% от баланса)
- 💸 **Точный расчёт комиссий** на основе изменений балансов
- 🔑 **Безопасность** - проверка секретного ключа
- 🧪 **Тестовый режим** для безопасного тестирования
- 📝 **Детальное логирование** всех операций

## 🚀 Быстрый старт

### Локальная установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/your-username/trading-bot.git
cd trading-bot
```

2. **Установите зависимости**
```bash
pip install -r requirements.txt
```

3. **Настройте переменные окружения**
```bash
cp .env.example .env
# Отредактируйте .env файл
```

4. **Запустите бота**
```bash
# Тестовый режим
python -m uvicorn bot.main:app --host 0.0.0.0 --port 8000

# Боевой режим
TEST_MODE=False python -m uvicorn bot.main:app --host 0.0.0.0 --port 8000
```

### Развёртывание на Render.com

1. **Fork репозиторий** на GitHub
2. **Создайте новый Web Service** на Render.com
3. **Подключите ваш GitHub репозиторий**
4. **Настройте переменные окружения** в Render Dashboard
5. **Deploy!**

## ⚙️ Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Основные настройки
TEST_MODE=True
WEBHOOK_SECRET=your_secret_key_here
DEFAULT_EXCHANGE=bybit

# Тестовые балансы (только для TEST_MODE=True)
TEST_BALANCE_USDT=1000

# API ключи Bybit (только для TEST_MODE=False)
API_KEY_BYBIT=your_bybit_api_key
API_SECRET_BYBIT=your_bybit_secret

# API ключи Binance (только для TEST_MODE=False)
API_KEY_BINANCE=your_binance_api_key
API_SECRET_BINANCE=your_binance_secret

# Комиссии (опционально)
BYBIT_FEE=0.001
BINANCE_FEE=0.001
```

### Настройка TradingView

1. **Создайте Pine Script** для генерации сигналов
2. **Настройте webhook** в TradingView Alert
3. **Используйте следующий формат**:

```javascript
// Для покупки
{
  "secret": "your_secret_key_here",
  "action": "buy",
  "symbol": "{{ticker}}",
  "usdt_amount": "{{usdtAmount}}"
}

// Для продажи
{
  "secret": "your_secret_key_here",
  "action": "sell",
  "symbol": "{{ticker}}"
}
```

## 📡 API Endpoints

### POST /webhook
Основной endpoint для получения сигналов от TradingView.

**Пример запроса:**
```json
{
  "secret": "your_secret_key",
  "action": "buy",
  "symbol": "BTCUSDT",
  "usdt_amount": 100
}
```

**Ответ:**
```json
{
  "status": "ok",
  "request_id": "20250815_123456_BTCUSDT_BUY",
  "exchange": "Bybit",
  "order": {
    "status": "filled",
    "side": "buy",
    "symbol": "BTCUSDT",
    "qty": 0.001,
    "price": 50000.0,
    "fee": 0.05
  },
  "balance_after": 950.0,
  "profit": null
}
```

### GET /status
Проверка статуса API.

### GET /balances
Получение текущих балансов.

## 🏗️ Архитектура

```
bot/
├── main.py              # FastAPI приложение
├── webhook.py           # Webhook endpoint
├── config.py            # Конфигурация
├── db.py               # Работа с базой данных
├── utils.py            # Утилиты
├── exchange_selector.py # Выбор биржи
└── exchanges/
    ├── bybit.py        # Bybit API
    └── binance.py      # Binance API
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Базовые тесты
python test_bot.py

# Тест webhook
python test_webhook.py

# Тест выбора биржи
python test_exchange_selector.py

# Тест сценариев с балансами
python test_balance_scenario.py

# Демонстрация
python demo_v3.py
```

### Тестовые данные
В тестовом режиме используются фейковые данные:
- Цены: Bybit=100.0, Binance=25000.0
- Балансы: настраиваются через TEST_BALANCE_USDT
- Сделки: симулируются без реальных API вызовов

## 🔒 Безопасность

- ✅ Проверка секретного ключа для всех webhook запросов
- ✅ Ограничение размера позиций (10% от баланса)
- ✅ Валидация входных данных
- ✅ Обработка ошибок API
- ✅ Логирование всех операций

## 📊 Мониторинг

### Логи
Все операции логируются с помощью `loguru`:
- Выбор биржи
- Выполнение сделок
- Ошибки и исключения
- Изменения балансов

### База данных
SQLite база данных содержит:
- Таблица `trades` - все сделки
- Таблица `balances` - текущие балансы

## 🚀 Развёртывание

### Render.com
1. Создайте новый Web Service
2. Подключите GitHub репозиторий
3. Настройте переменные окружения
4. Укажите команду запуска: `python -m uvicorn bot.main:app --host 0.0.0.0 --port $PORT`

### Docker (опционально)
```bash
docker build -t trading-bot .
docker run -p 8000:8000 --env-file .env trading-bot
```

## 📈 Версии

- **v3.0** - Умный выбор биржи с учётом балансов
- **v2.0** - Автоматический выбор биржи по цене
- **v1.0** - Базовая функциональность

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## ⚠️ Отказ от ответственности

Этот бот предназначен для образовательных целей. Торговля криптовалютами связана с высокими рисками. Используйте на свой страх и риск.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
- Создайте Issue на GitHub
- Проверьте документацию в папке `docs/`
- Изучите примеры в папке `examples/`

---

**Удачной торговли! 🚀**
