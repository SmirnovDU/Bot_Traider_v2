#!/usr/bin/env python3

import os
import sys
import sqlite3
import mysql.connector
from datetime import datetime

# Добавляем путь к модулям
sys.path.append('bot')

def migrate_sqlite_to_mysql():
    """Миграция данных из SQLite в MySQL"""
    
    # Параметры подключения к MySQL (настройте под ваш Railway MySQL)
    MYSQL_CONFIG = {
        'host': input("MySQL Host (Railway): "),
        'port': int(input("MySQL Port (обычно 3306): ") or "3306"),
        'user': input("MySQL User: "),
        'password': input("MySQL Password: "),
        'database': input("MySQL Database (trading_bot): ") or "trading_bot"
    }
    
    print("\n🔄 Начинаем миграцию...")
    
    try:
        # Подключаемся к SQLite
        sqlite_path = "bot/trades.db"
        if not os.path.exists(sqlite_path):
            print(f"❌ SQLite база данных не найдена: {sqlite_path}")
            return
            
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cur = sqlite_conn.cursor()
        
        # Подключаемся к MySQL
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        mysql_cur = mysql_conn.cursor()
        
        print("✅ Подключение к базам данных установлено")
        
        # Создаём таблицы в MySQL
        print("📋 Создание таблиц в MySQL...")
        
        mysql_cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id VARCHAR(255) UNIQUE NOT NULL,
            timestamp DATETIME NOT NULL,
            exchange VARCHAR(50),
            side VARCHAR(10),
            symbol VARCHAR(50),
            price DECIMAL(20,8),
            qty DECIMAL(20,8),
            amount_usdt DECIMAL(20,8),
            fee DECIMAL(20,8),
            profit DECIMAL(20,8),
            balance_after DECIMAL(20,8),
            note TEXT,
            INDEX idx_exchange_symbol (exchange, symbol),
            INDEX idx_side (side),
            INDEX idx_timestamp (timestamp)
        )
        """)
        
        mysql_cur.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            exchange VARCHAR(50),
            coin VARCHAR(20),
            amount DECIMAL(20,8),
            PRIMARY KEY (exchange, coin)
        )
        """)
        
        # Миграция сделок
        print("📊 Миграция сделок...")
        sqlite_cur.execute("SELECT * FROM trades")
        trades = sqlite_cur.fetchall()
        
        # Получаем названия колонок
        sqlite_cur.execute("PRAGMA table_info(trades)")
        columns = [col[1] for col in sqlite_cur.fetchall()]
        print(f"Колонки SQLite: {columns}")
        
        migrated_trades = 0
        for trade in trades:
            try:
                # Преобразуем timestamp если нужно
                timestamp = trade[columns.index('timestamp')]
                if isinstance(timestamp, str):
                    # Пытаемся парсить ISO формат
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now()
                
                mysql_cur.execute("""
                INSERT IGNORE INTO trades 
                (request_id, timestamp, exchange, side, symbol, price, qty, 
                 amount_usdt, fee, profit, balance_after, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    trade[columns.index('request_id')],
                    timestamp,
                    trade[columns.index('exchange')],
                    trade[columns.index('side')],
                    trade[columns.index('symbol')],
                    trade[columns.index('price')],
                    trade[columns.index('qty')],
                    trade[columns.index('amount_usdt')],
                    trade[columns.index('fee')],
                    trade[columns.index('profit')],
                    trade[columns.index('balance_after')],
                    trade[columns.index('note')] if 'note' in columns else None
                ))
                migrated_trades += 1
            except Exception as e:
                print(f"⚠️ Ошибка миграции сделки: {e}")
        
        # Миграция балансов
        print("💰 Миграция балансов...")
        sqlite_cur.execute("SELECT * FROM balances")
        balances = sqlite_cur.fetchall()
        
        migrated_balances = 0
        for balance in balances:
            try:
                mysql_cur.execute("""
                INSERT INTO balances (exchange, coin, amount) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE amount=%s
                """, (balance[0], balance[1], balance[2], balance[2]))
                migrated_balances += 1
            except Exception as e:
                print(f"⚠️ Ошибка миграции баланса: {e}")
        
        # Подтверждаем изменения
        mysql_conn.commit()
        
        # Проверяем результат
        mysql_cur.execute("SELECT COUNT(*) FROM trades")
        mysql_trades_count = mysql_cur.fetchone()[0]
        
        mysql_cur.execute("SELECT COUNT(*) FROM balances")
        mysql_balances_count = mysql_cur.fetchone()[0]
        
        print(f"\n✅ Миграция завершена!")
        print(f"📊 Сделки: {migrated_trades} перенесено, {mysql_trades_count} всего в MySQL")
        print(f"💰 Балансы: {migrated_balances} перенесено, {mysql_balances_count} всего в MySQL")
        
        # Показываем последние сделки
        mysql_cur.execute("""
        SELECT exchange, side, symbol, amount_usdt, timestamp 
        FROM trades ORDER BY timestamp DESC LIMIT 5
        """)
        recent_trades = mysql_cur.fetchall()
        
        print(f"\n📋 Последние 5 сделок в MySQL:")
        for trade in recent_trades:
            print(f"  {trade[4]} - {trade[1].upper()} {trade[2]} на {trade[0]} (${trade[3]})")
        
        # Показываем балансы
        mysql_cur.execute("SELECT exchange, coin, amount FROM balances WHERE amount > 0")
        active_balances = mysql_cur.fetchall()
        
        print(f"\n💰 Активные балансы в MySQL:")
        for balance in active_balances:
            print(f"  {balance[0]} - {balance[1]}: {balance[2]}")
        
        # Закрываем соединения
        sqlite_conn.close()
        mysql_conn.close()
        
        print(f"\n🎯 Готово! Теперь обновите переменные окружения:")
        print(f"MYSQL_HOST={MYSQL_CONFIG['host']}")
        print(f"MYSQL_PORT={MYSQL_CONFIG['port']}")
        print(f"MYSQL_USER={MYSQL_CONFIG['user']}")
        print(f"MYSQL_PASSWORD={MYSQL_CONFIG['password']}")
        print(f"MYSQL_DATABASE={MYSQL_CONFIG['database']}")
        print(f"USE_MYSQL=true")
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🗄️ Миграция данных из SQLite в MySQL")
    print("Убедитесь что ваш Railway MySQL контейнер запущен и доступен")
    print()
    
    migrate_sqlite_to_mysql()
