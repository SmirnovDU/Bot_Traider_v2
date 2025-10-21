# 🔐 Настройка переменных окружения

## Быстрая настройка

### 1. Создайте файл .env:
```bash
cp env.example .env
```

### 2. Отредактируйте .env файл:
```bash
# API ключи для бирж
BINANCE_API_KEY=ваш_api_ключ_binance
BINANCE_SECRET_KEY=ваш_секретный_ключ_binance
BINANCE_TESTNET=false

BYBIT_API_KEY=ваш_api_ключ_bybit
BYBIT_SECRET_KEY=ваш_секретный_ключ_bybit
BYBIT_TESTNET=false

# Telegram настройки
TELEGRAM_BOT_TOKEN=ваш_токен_telegram_бота
TELEGRAM_CHAT_ID=ваш_chat_id

# Дополнительные настройки
DEFAULT_EXCHANGE=binance
SIMULATION_MODE=true
```

## 🔑 Получение API ключей

### Binance:
1. Зайдите на [binance.com](https://binance.com)
2. Создайте аккаунт и пройдите верификацию
3. Перейдите в API Management
4. Создайте новый API ключ
5. **Важно**: Дайте только права на Spot Trading, НЕ давайте права на Withdraw!

### Bybit:
1. Зайдите на [bybit.com](https://bybit.com)
2. Создайте аккаунт и пройдите верификацию
3. Перейдите в API Management
4. Создайте новый API ключ
5. **Важно**: Дайте только права на Spot Trading

## 📱 Настройка Telegram

### 1. Создание бота:
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Сохраните токен бота

### 2. Получение Chat ID:
1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Бот пришлет ваш Chat ID

## 🛡️ Безопасность

### ⚠️ Важные правила:
- **Никогда не делитесь** API ключами
- **Не коммитьте** .env файл в git
- **Используйте тестовые сети** для начала
- **Ограничьте права** API ключей

### 🔒 Права API ключей:
- ✅ Spot Trading (торговля)
- ❌ Withdraw (вывод средств)
- ❌ Futures (фьючерсы)
- ❌ Margin (маржинальная торговля)

## 🚀 Запуск

После настройки .env файла:
```bash
python3 autonomous_trading_bot.py
```

## 🆘 Проблемы

### "API ключ не работает":
- Проверьте правильность ключа
- Убедитесь в правах доступа
- Проверьте IP whitelist (если настроен)

### "Telegram не работает":
- Проверьте токен бота
- Убедитесь в правильности Chat ID
- Добавьте бота в чат

### "Не удается подключиться":
- Проверьте интернет соединение
- Убедитесь в доступности биржи
- Проверьте настройки testnet

