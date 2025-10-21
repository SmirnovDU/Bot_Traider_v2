# 🤖 Автономный торговый бот v2.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/github/stars/SmirnovDU/Bot_Traider_v2?style=social)](https://github.com/SmirnovDU/Bot_Traider_v2)

> Полностью автономный торговый бот для Binance и Bybit без TradingView

## ✨ Особенности

- 🚀 **Полная автономность** - работает без TradingView
- 📊 **8 технических индикаторов** - EMA, ADX, MACD, RSI, TSI, KDJ, VWAP, ATR
- 🏢 **Поддержка бирж** - Binance и Bybit через ccxt
- ⚙️ **Гибкая настройка** - включение/выключение индикаторов
- 🎮 **Режимы работы** - симуляция и реальная торговля
- 📱 **Telegram интеграция** - полные уведомления
- 🔐 **Безопасность** - API ключи в переменных окружения

## 🚀 Быстрый запуск

```bash
# Клонирование
git clone https://github.com/SmirnovDU/Bot_Traider_v2.git
cd Bot_Traider_v2

# Установка зависимостей
pip install -r requirements.txt

# Настройка
cp env.example .env
# Отредактируйте .env файл с вашими ключами

# Проверка готовности
python3 quick_test.py

# Запуск бота
python3 autonomous_trading_bot.py
```

## 📁 Структура проекта

```
Trade/
├── autonomous_trading_bot.py    # Главный файл бота
├── run_bot.py                   # Скрипт запуска
├── quick_test.py                # Быстрая проверка
├── test_bot.py                  # Полное тестирование
├── config.yaml                  # Конфигурация
├── requirements.txt             # Зависимости
├── bot/                         # Модули бота
│   ├── data_fetcher.py         # Получение данных
│   ├── indicators.py           # Расчет индикаторов
│   ├── strategy.py             # Торговая стратегия
│   ├── trading_engine.py       # Исполнение ордеров
│   └── notifications.py        # Уведомления
└── docs/                       # Документация
    └── API.md
```

## 📊 Особенности

- **Автономность**: Работает без TradingView
- **Индикаторы**: EMA, ADX, MACD, RSI, TSI, KDJ, VWAP, ATR
- **Биржи**: Binance и Bybit
- **Режимы**: Симуляция и реальная торговля
- **Уведомления**: Telegram интеграция

## 🛡️ Безопасность

- По умолчанию: симуляция (безопасно)
- API ключи не обязательны для симуляции
- Начните с симуляции перед реальной торговлей

### Настройка:
```bash
cp env.example .env
# Отредактируйте .env файл с вашими ключами
```

## 📚 Документация

- `README_AUTONOMOUS_BOT.md` - Полная документация
- `START_HERE.md` - Быстрый старт
- `ЗАПУСК_БОТА.md` - Инструкции по запуску

## ⚠️ Отказ от ответственности

Торговля криптовалютами связана с рисками. Используйте на свой страх и риск!
