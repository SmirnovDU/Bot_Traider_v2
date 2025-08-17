#!/usr/bin/env python3
"""
Миграция: добавление поля profit_no_fees в таблицу trades
"""

import os
import sys

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from bot.config import USE_MYSQL, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
    import mysql.connector
    from loguru import logger
    
    def migrate_mysql():
        """Добавляем поле profit_no_fees в MySQL"""
        if not USE_MYSQL:
            print("❌ MySQL не используется, миграция не нужна")
            return False
            
        print("🔄 Миграция MySQL: добавление поля profit_no_fees")
        
        try:
            # Подключаемся к MySQL
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            cur = conn.cursor()
            
            # Проверяем, есть ли уже поле profit_no_fees
            cur.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
              AND TABLE_NAME = 'trades' 
              AND COLUMN_NAME = 'profit_no_fees'
            """, (MYSQL_DATABASE,))
            
            if cur.fetchone():
                print("✅ Поле profit_no_fees уже существует")
                return True
            
            # Добавляем поле
            print("➕ Добавляем поле profit_no_fees...")
            cur.execute("""
            ALTER TABLE trades 
            ADD COLUMN profit_no_fees DECIMAL(20,8) AFTER profit
            """)
            
            conn.commit()
            conn.close()
            print("✅ Миграция завершена успешно")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Ошибка миграции MySQL: {err}")
            return False
            
    if __name__ == "__main__":
        migrate_mysql()
        
except ImportError:
    print("❌ MySQL модули не установлены, миграция невозможна")
