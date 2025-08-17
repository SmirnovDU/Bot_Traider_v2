"""
Система миграций базы данных.
Автоматически применяет изменения схемы при запуске бота.
"""

from loguru import logger
from bot.config import USE_MYSQL


def get_table_columns(cur, table_name):
    """Получить список столбцов таблицы"""
    if USE_MYSQL:
        cur.execute(f"DESCRIBE {table_name}")
        return [row[0] for row in cur.fetchall()]
    else:
        cur.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cur.fetchall()]


def add_column_if_not_exists(cur, table_name, column_name, column_definition):
    """Добавить столбец если его нет"""
    existing_columns = get_table_columns(cur, table_name)
    
    if column_name not in existing_columns:
        if USE_MYSQL:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        else:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        
        logger.info(f"🔧 Добавляем столбец {column_name} в таблицу {table_name}")
        cur.execute(sql)
        return True
    else:
        logger.debug(f"✅ Столбец {column_name} уже существует в таблице {table_name}")
        return False


def apply_migrations():
    """Применить все миграции"""
    logger.info("🔄 Проверяем необходимость миграций...")
    
    if USE_MYSQL:
        apply_mysql_migrations()
    else:
        apply_sqlite_migrations()


def apply_mysql_migrations():
    """Применить миграции для MySQL"""
    try:
        import mysql.connector
        from bot.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
        
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cur = conn.cursor()
        
        migrations_applied = 0
        
        # Миграция 1: Добавление profit_no_fees в trades
        if add_column_if_not_exists(cur, "trades", "profit_no_fees", "DECIMAL(20,8)"):
            migrations_applied += 1
        
        # Миграция 2: Добавление индексов для производительности
        try:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_exchange_symbol ON trades(exchange, symbol)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_side ON trades(side)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
            logger.debug("✅ Индексы проверены/созданы")
        except mysql.connector.Error as e:
            if "Duplicate key name" not in str(e):
                logger.warning(f"Предупреждение при создании индексов: {e}")
        
        # Миграция 3: Добавление request_id уникального ключа если его нет
        try:
            cur.execute("ALTER TABLE trades ADD UNIQUE KEY uk_request_id (request_id)")
            logger.info("🔧 Добавлен уникальный ключ для request_id")
            migrations_applied += 1
        except mysql.connector.Error as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                logger.debug("✅ Уникальный ключ request_id уже существует")
            else:
                logger.warning(f"Предупреждение при создании уникального ключа: {e}")
        
        # Будущие миграции добавлять здесь...
        # if add_column_if_not_exists(cur, "trades", "new_column", "VARCHAR(255)"):
        #     migrations_applied += 1
        
        conn.commit()
        conn.close()
        
        if migrations_applied > 0:
            logger.info(f"✅ Применено {migrations_applied} миграций MySQL")
        else:
            logger.info("✅ Все миграции MySQL уже применены")
            
    except Exception as e:
        logger.error(f"❌ Ошибка применения миграций MySQL: {e}")
        raise


def apply_sqlite_migrations():
    """Применить миграции для SQLite"""
    try:
        import sqlite3
        from bot.config import DB_PATH
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        migrations_applied = 0
        
        # Миграция 1: Добавление profit_no_fees в trades
        if add_column_if_not_exists(cur, "trades", "profit_no_fees", "REAL"):
            migrations_applied += 1
        
        # Миграция 2: Добавление индексов для производительности  
        try:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_exchange_symbol ON trades(exchange, symbol)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_side ON trades(side)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
            logger.debug("✅ Индексы SQLite проверены/созданы")
        except sqlite3.Error as e:
            logger.warning(f"Предупреждение при создании индексов SQLite: {e}")
        
        # Будущие миграции добавлять здесь...
        # if add_column_if_not_exists(cur, "trades", "new_column", "TEXT"):
        #     migrations_applied += 1
        
        conn.commit()
        conn.close()
        
        if migrations_applied > 0:
            logger.info(f"✅ Применено {migrations_applied} миграций SQLite")
        else:
            logger.info("✅ Все миграции SQLite уже применены")
            
    except Exception as e:
        logger.error(f"❌ Ошибка применения миграций SQLite: {e}")
        raise


def create_migration_template(migration_name):
    """Создать шаблон для новой миграции"""
    template = f'''
# Миграция: {migration_name}
# Добавить в apply_mysql_migrations() и apply_sqlite_migrations():

# Для MySQL:
if add_column_if_not_exists(cur, "table_name", "column_name", "COLUMN_TYPE"):
    migrations_applied += 1

# Для SQLite:  
if add_column_if_not_exists(cur, "table_name", "column_name", "COLUMN_TYPE"):
    migrations_applied += 1
'''
    
    print(template)
    return template


if __name__ == "__main__":
    # Тест миграций
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    print("🧪 Тестирование системы миграций")
    apply_migrations()
