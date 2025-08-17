# 🔄 Система миграций базы данных

## Как работает

При каждом запуске бота автоматически проверяется актуальность схемы БД и применяются необходимые изменения.

## Файлы системы миграций

- `bot/migrations.py` - основная логика миграций
- `migrate_add_profit_no_fees.py` - старый скрипт (можно удалить)

## Как добавить новую миграцию

### 1. Добавить в bot/migrations.py

**Для MySQL** (в функции `apply_mysql_migrations()`):
```python
# Миграция N: Описание изменения
if add_column_if_not_exists(cur, "trades", "new_column", "VARCHAR(255)"):
    migrations_applied += 1
```

**Для SQLite** (в функции `apply_sqlite_migrations()`):
```python
# Миграция N: Описание изменения  
if add_column_if_not_exists(cur, "trades", "new_column", "TEXT"):
    migrations_applied += 1
```

### 2. Примеры типов данных

| Назначение | MySQL | SQLite |
|------------|-------|---------|
| Строка | `VARCHAR(255)` | `TEXT` |
| Число | `DECIMAL(20,8)` | `REAL` |
| Целое | `INT` | `INTEGER` |
| Дата/время | `DATETIME` | `TEXT` |
| Логическое | `BOOLEAN` | `INTEGER` |

### 3. Пример миграции

```python
# Добавляем столбец для статуса сделки
if add_column_if_not_exists(cur, "trades", "status", "VARCHAR(20) DEFAULT 'completed'"):
    migrations_applied += 1

# Добавляем таблицу настроек
cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key_name VARCHAR(50) PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
```

## Принципы работы

✅ **Безопасность**: Миграции только добавляют столбцы, не удаляют  
✅ **Идемпотентность**: Можно запускать много раз без проблем  
✅ **Автоматизация**: Выполняются при каждом запуске бота  
✅ **Логирование**: Все изменения записываются в логи  

## Какие миграции уже применены

1. **profit_no_fees** - столбец для анализа стратегии БЕЗ комиссий
2. **Индексы** - для улучшения производительности запросов
3. **Уникальный ключ** - для request_id (предотвращение дубликатов)

## Тестирование

```bash
# Локальное тестирование SQLite
USE_MYSQL=false python3 bot/migrations.py

# Проверка на продакшене (Railway автоматически)
# Смотрим логи запуска бота
```

## В будущем можно добавить

- Столбец `execution_time` для времени выполнения сделки
- Таблицу `bot_settings` для конфигурации
- Столбец `strategy_version` для версионирования стратегий
- И многое другое...

Система готова к любым изменениям схемы БД! 🚀
