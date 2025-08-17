#!/usr/bin/env python3
"""
Дебаг сохранения сделок в MySQL
"""

import os
import sys
from datetime import datetime, timezone

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def debug_save_trade():
    """Отладка сохранения сделки в MySQL"""
    print("🔍 Дебаг сохранения сделок в MySQL")
    
    # Проверяем доступность MySQL
    try:
        from bot.config import USE_MYSQL, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
        print(f"   USE_MYSQL: {USE_MYSQL}")
        print(f"   MYSQL_HOST: {MYSQL_HOST}")
        print(f"   MYSQL_DATABASE: {MYSQL_DATABASE}")
        
        if not USE_MYSQL:
            print("   ❌ MySQL не используется")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка конфигурации: {e}")
        return False
    
    # Проверяем подключение к MySQL
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print("   ✅ Подключение к MySQL успешно")
        
        # Проверяем структуру таблицы trades
        cur = conn.cursor()
        cur.execute("DESCRIBE trades")
        columns = cur.fetchall()
        print("\n📋 Структура таблицы trades:")
        for col in columns:
            print(f"   {col[0]} - {col[1]}")
            
        # Проверяем есть ли поле profit_no_fees
        column_names = [col[0] for col in columns]
        if 'profit_no_fees' not in column_names:
            print("   ❌ Поле profit_no_fees отсутствует!")
            return False
        else:
            print("   ✅ Поле profit_no_fees присутствует")
            
        # Проверяем количество записей
        cur.execute("SELECT COUNT(*) FROM trades")
        trades_count = cur.fetchone()[0]
        print(f"\n📊 Количество записей в trades: {trades_count}")
        
        # Показываем последние 3 записи
        cur.execute("SELECT request_id, timestamp, exchange, side, symbol FROM trades ORDER BY timestamp DESC LIMIT 3")
        recent_trades = cur.fetchall()
        if recent_trades:
            print("\n🕒 Последние 3 сделки:")
            for trade in recent_trades:
                print(f"   {trade[0]} - {trade[2]} {trade[3]} {trade[4]}")
        else:
            print("   📭 Нет записей в таблице")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Ошибка подключения к MySQL: {e}")
        return False
    
    # Тестируем сохранение новой сделки
    try:
        from bot.db import save_trade
        from bot.utils import generate_request_id
        
        print("\n💾 Тестируем сохранение новой сделки...")
        
        request_id = generate_request_id("TESTUSDT", "buy")
        test_trade = {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": "Bybit",
            "side": "buy", 
            "symbol": "TESTUSDT",
            "price": 1.0,
            "qty": 10.0,
            "amount_usdt": 10.0,
            "fee": 0.0,
            "profit": None,
            "profit_no_fees": None,
            "balance_after": 990.0,
            "note": "Debug test trade"
        }
        
        save_trade(test_trade)
        print(f"   ✅ Сделка {request_id} сохранена")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка тестового сохранения: {e}")
        return False

if __name__ == "__main__":
    debug_save_trade()
