# 🚀 Деплой на Railway

## Быстрый деплой

### 1. Подготовка
```bash
# Клонируйте репозиторий
git clone https://github.com/SmirnovDU/Bot_Traider_v2.git
cd Bot_Traider_v2
```

### 2. Настройка Railway

1. Зайдите на [railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Railway автоматически определит Python проект

### 3. Переменные окружения

В Railway Dashboard → Variables добавьте:

```bash
# API ключи (обязательно для реальной торговли)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=false

# Telegram (опционально)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Настройки
DEFAULT_EXCHANGE=binance
SIMULATION_MODE=true
```

### 4. Деплой

Railway автоматически:
- Установит зависимости из `requirements.txt`
- Запустит `railway.py`
- Настроит healthcheck на `/health`

## 🔧 Конфигурация

### Railway.yaml
```yaml
version: 2
build:
  builder: NIXPACKS
deploy:
  startCommand: python railway.py
  healthcheckPath: /health
  healthcheckTimeout: 100
```

### Procfile
```
web: python railway.py
```

## 📊 Мониторинг

### Healthcheck
- **URL**: `https://your-app.railway.app/health`
- **Ответ**: `{"status": "ok", "service": "autonomous_trading_bot", "version": "2.0"}`

### Логи
- Просматривайте логи в Railway Dashboard
- Логи бота сохраняются в `bot.log`

## 🛡️ Безопасность

### Переменные окружения
- ✅ API ключи в переменных окружения
- ✅ Никогда не коммитьте .env файл
- ✅ Используйте Railway Variables

### Рекомендации
- Начните с `SIMULATION_MODE=true`
- Используйте тестовые сети (`TESTNET=true`)
- Ограничьте права API ключей

## 🆘 Проблемы

### "Error loading ASGI app"
- ✅ Исправлено: используйте `railway.py` вместо `bot.main`

### "Module not found"
- Проверьте, что все файлы загружены
- Убедитесь в правильности `requirements.txt`

### "Healthcheck failed"
- Проверьте переменные окружения
- Убедитесь в доступности `/health` endpoint

### "Bot not starting"
- Проверьте API ключи
- Убедитесь в правильности конфигурации
- Проверьте логи в Railway Dashboard

## 📈 Масштабирование

### Ресурсы
- **CPU**: 0.5 vCPU (достаточно для бота)
- **RAM**: 1GB (рекомендуется)
- **Storage**: 1GB (для логов)

### Мониторинг
- Используйте Railway Metrics
- Настройте алерты в Telegram
- Мониторьте использование ресурсов

## 🔄 Обновления

### Автоматические
- Railway автоматически деплоит при push в main
- Используйте GitHub Actions для CI/CD

### Ручные
```bash
# Локальные изменения
git add .
git commit -m "Update bot"
git push origin main

# Railway автоматически обновит
```

## 📚 Дополнительно

### Логи
```bash
# Просмотр логов в Railway CLI
railway logs
```

### Переменные
```bash
# Установка переменных через CLI
railway variables set BINANCE_API_KEY=your_key
```

### SSH доступ
```bash
# Подключение к контейнеру
railway shell
```
