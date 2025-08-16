#!/usr/bin/env python3

import os
import sys

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

def reset_database():
    """Полный сброс базы данных (ВНИМАНИЕ: удаляет все данные!)"""
    print("⚠️ ВНИМАНИЕ: Этот скрипт полностью удалит все данные из БД!")
    
    confirm = input("Введите 'YES' для подтверждения: ")
    if confirm != "YES":
        print("❌ Операция отменена.")
        return
    
    from bot.config import DB_PATH
    import sqlite3
    
    try:
        # Удаляем файл БД
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"🗑️ Файл БД удален: {DB_PATH}")
        
        # Пересоздаем БД
        from bot.db import init_db, init_test_balances
        init_db()
        init_test_balances()
        
        print("✅ База данных пересоздана с нуля!")
        print("📊 Тестовые балансы инициализированы.")
        
        # Показываем статус
        from bot.db import get_all_balances, get_trades_summary
        balances = get_all_balances()
        trades = get_trades_summary()
        
        print(f"\n📈 Текущие балансы:")
        for balance in balances:
            print(f"  {balance['exchange']} - {balance['coin']}: {balance['amount']}")
        
        print(f"📜 Сделки: {trades['total_trades']}")
        
    except Exception as e:
        print(f"❌ Ошибка при сбросе БД: {e}")

if __name__ == "__main__":
    reset_database()
