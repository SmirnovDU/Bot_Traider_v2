# Версия 1.1 - Планы развития

## Новые возможности

### 1. Стоп-лоссы и тейк-профиты (15%)

#### Фоновый мониторинг позиций
- Отдельный процесс для мониторинга открытых позиций
- Автоматическое закрытие при достижении 15% прибыли/убытка
- Настройка процентов через конфигурацию

#### Реализация
```python
# Новый модуль: bot/monitor.py
class PositionMonitor:
    def __init__(self):
        self.active_positions = {}
    
    def add_position(self, symbol, entry_price, qty, side):
        # Добавление позиции для мониторинга
    
    def check_positions(self):
        # Проверка всех активных позиций
        # Закрытие при достижении лимитов
```

### 2. Telegram бот для уведомлений

#### Функции
- Уведомления о покупке/продаже
- Текущие балансы
- Статистика торговли
- Управление ботом (старт/стоп)

#### Команды
```
/start - Запуск бота
/status - Статус бота
/balances - Текущие балансы
/statistics - Статистика торговли
/stop - Остановка бота
```

#### Реализация
```python
# Новый модуль: bot/telegram_bot.py
from telegram.ext import Updater, CommandHandler, MessageHandler

class TradingBotTelegram:
    def __init__(self, token):
        self.updater = Updater(token)
        self.setup_handlers()
    
    def send_notification(self, message):
        # Отправка уведомлений пользователям
```

## Структура проекта v1.1

```
Trade/
├── bot/
│   ├── config.py          # Обновлённая конфигурация
│   ├── db.py              # Расширенная БД
│   ├── main.py            # Основной файл
│   ├── webhook.py         # Webhook обработчик
│   ├── utils.py           # Утилиты
│   ├── monitor.py         # НОВЫЙ: Мониторинг позиций
│   ├── telegram_bot.py    # НОВЫЙ: Telegram бот
│   └── exchanges/
│       ├── bybit.py       # Обновлённый
│       └── binance.py     # Обновлённый
├── requirements.txt       # Обновлённые зависимости
├── .env.example          # Обновлённый пример
└── README.md             # Обновлённая документация
```

## Новые зависимости

```txt
# Добавить в requirements.txt
python-telegram-bot==13.7
schedule==1.1.0
```

## Расширение базы данных

### Новая таблица: positions
```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    entry_price REAL,
    current_price REAL,
    qty REAL,
    side TEXT,
    entry_time TEXT,
    take_profit REAL,
    stop_loss REAL,
    status TEXT DEFAULT 'open'
);
```

### Обновление таблицы trades
```sql
-- Добавить поле для связи с позицией
ALTER TABLE trades ADD COLUMN position_id INTEGER;
```

## Конфигурация v1.1

```env
# Существующие настройки...

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Мониторинг позиций
TAKE_PROFIT_PERCENT=15.0
STOP_LOSS_PERCENT=15.0
MONITOR_INTERVAL=30  # секунды

# Уведомления
ENABLE_TELEGRAM_NOTIFICATIONS=True
ENABLE_EMAIL_NOTIFICATIONS=False
```

## API Endpoints v1.1

### Новые endpoints
```
GET /positions - Активные позиции
POST /positions/{id}/close - Закрыть позицию
GET /statistics - Статистика торговли
POST /bot/start - Запустить бота
POST /bot/stop - Остановить бота
```

## Поток работы v1.1

1. **Получение сигнала** → Webhook
2. **Создание позиции** → Запись в БД + Telegram уведомление
3. **Мониторинг** → Фоновый процесс проверяет цены
4. **Закрытие позиции** → При достижении лимитов + Telegram уведомление
5. **Обновление статистики** → Расчёт P&L

## Безопасность v1.1

- Валидация Telegram токенов
- Ограничение доступа к API
- Логирование всех действий
- Резервное копирование БД

## Мониторинг v1.1

### Telegram уведомления
- Покупка/продажа
- Достижение лимитов
- Ошибки системы
- Ежедневная статистика

### Логирование
- Все операции с позициями
- Telegram взаимодействия
- Ошибки мониторинга

## Тестирование v1.1

```bash
# Новые тесты
python3 test_monitor.py      # Тест мониторинга
python3 test_telegram.py     # Тест Telegram бота
python3 test_positions.py    # Тест позиций
```

## Миграция с v1.0

1. Обновить зависимости
2. Добавить новые таблицы в БД
3. Настроить Telegram бота
4. Запустить мониторинг
5. Протестировать функциональность

## Планы на будущее

### Версия 1.2
- Поддержка других бирж (OKX, KuCoin)
- Веб-интерфейс для управления
- Бэктестинг стратегий
- Машинное обучение для оптимизации

### Версия 2.0
- Мультистратегийность
- Портфельное управление
- Риск-менеджмент
- Интеграция с другими источниками сигналов
