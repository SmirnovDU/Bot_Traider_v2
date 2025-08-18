# Настройка TradingView Алертов для Improved EMA Strategy

## 📋 Текущая стратегия: `TradingView_improved.txt`

Стратегия использует `alertcondition()` с константными значениями для совместимости с Pine Script.

## 🔧 Настройка алертов в TradingView

### Шаг 1: Загрузка стратегии
1. Откройте TradingView
2. Перейдите в Pine Editor
3. Загрузите файл `TradingView_improved.txt`
4. Нажмите "Add to Chart"

### Шаг 2: Создание алертов

#### Для покупок (Buy):
1. Нажмите на колокольчик 🔔 рядом с названием стратегии
2. Выберите "Create Alert"
3. Настройте:
   - **Condition**: "Improved EMA Cross with Filters v7"
   - **Trigger**: "Buy Webhook Signal"
   - **Message**: 
   ```json
   {"secret":"kljGCCKJS78ef6vLKGA88","action":"buy","symbol":"{{ticker}}","usdt_amount":"10","exchange":"bybit"}
   ```
   - **Webhook URL**: `https://your-bot-url.com/webhook`

#### Для продаж (Sell):
1. Создайте второй алерт
2. Настройте:
   - **Condition**: "Improved EMA Cross with Filters v7"
   - **Trigger**: "Sell Webhook Signal"
   - **Message**: 
   ```json
   {"secret":"kljGCCKJS78ef6vLKGA88","action":"sell","symbol":"{{ticker}}","usdt_amount":"10","exchange":"bybit"}
   ```
   - **Webhook URL**: `https://your-bot-url.com/webhook`

## ⚙️ Настройка параметров

### Изменение суммы торговли:
В поле **Message** замените `"usdt_amount":"10"` на нужную сумму:
```json
{"secret":"kljGCCKJS78ef6vLKGA88","action":"buy","symbol":"{{ticker}}","usdt_amount":"25","exchange":"bybit"}
```

### Изменение биржи:
В поле **Message** замените `"exchange":"bybit"` на нужную биржу:
```json
{"secret":"kljGCCKJS78ef6vLKGA88","action":"buy","symbol":"{{ticker}}","usdt_amount":"10","exchange":"binance"}
```

## 🎯 Доступные триггеры

1. **Buy Webhook Signal** - сигнал на покупку
2. **Sell Webhook Signal** - сигнал на продажу

## 📊 Параметры стратегии

В стратегии можно настроить:
- **EMA Fast/Slow** - периоды EMA (по умолчанию 20/50)
- **RSI Period** - период RSI (по умолчанию 14)
- **ATR Period** - период ATR (по умолчанию 14)
- **Sell Method** - метод продажи:
  - "EMA Cross" - только по пересечению EMA
  - "RSI Overbought" - по RSI перекупленности + стоп-лосс
  - "Combined" - комбинированный подход

## 🔍 Проверка работы

1. Запустите бэктест стратегии
2. Убедитесь, что сигналы появляются на графике
3. Проверьте, что алерты срабатывают при появлении сигналов
4. Убедитесь, что webhook-запросы доходят до бота

## ⚠️ Важные замечания

1. **Secret** должен совпадать с `WEBHOOK_SECRET` в `.env` файле бота
2. **Exchange** должен быть одним из: "bybit" или "binance"
3. **usdt_amount** должна быть числом в строковом формате
4. **{{ticker}}** автоматически подставляется TradingView

## 🚀 Альтернативный вариант с alert()

Если нужна большая гибкость, можно использовать версию с `alert()`:

```pine
if final_buy
    strategy.entry("Buy", strategy.long, qty=qty)
    alert('{"secret":"kljGCCKJS78ef6vLKGA88","action":"buy","symbol":"' + syminfo.ticker + '","usdt_amount":"' + str.tostring(usdtAmount) + '","exchange":"' + exchange_name + '"}')
```

Но тогда нужно:
1. Использовать триггер "On Order Fill" вместо "On Alert"
2. Настроить Message как `{{alert_message}}`
