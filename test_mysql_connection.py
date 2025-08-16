#!/usr/bin/env python3

import os
import sys

# Устанавливаем переменные для тестирования MySQL
os.environ['USE_MYSQL'] = 'True'
os.environ['TEST_MODE'] = 'True'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

def test_mysql_connection():
    """Тестирование подключения к MySQL и создания таблиц"""
    print("🗄️ Тестирование подключения к MySQL...")
    
    try:
        # Импортируем модуль БД
        from bot.db import init_db, init_test_balances, get_all_balances, save_trade
        from datetime import datetime, timezone
        
        print("✅ Модули импортированы успешно")
        
        # Инициализируем БД
        print("📋 Создание таблиц...")
        init_db()
        print("✅ Таблицы созданы/проверены")
        
        # Инициализируем тестовые балансы
        print("💰 Инициализация тестовых балансов...")
        init_test_balances()
        print("✅ Тестовые балансы инициализированы")
        
        # Проверяем балансы
        balances = get_all_balances()
        print(f"📊 Текущие балансы: {len(balances)}")
        for balance in balances:
            print(f"  {balance['exchange']} - {balance['coin']}: {balance['amount']}")
        
        # Создаем тестовую сделку
        print("🧪 Тестовая сделка...")
        test_trade = {
            "request_id": f"test_{int(datetime.now().timestamp())}_TESTUSDT_BUY",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": "Bybit",
            "side": "buy",
            "symbol": "TESTUSDT",
            "price": 1.0,
            "qty": 10.0,
            "amount_usdt": 10.0,
            "fee": 0.01,
            "profit": None,
            "balance_after": 990.0,
            "note": "MySQL connection test"
        }
        
        save_trade(test_trade)
        print("✅ Тестовая сделка сохранена")
        
        print("\n🎉 Все тесты пройдены! MySQL работает корректно.")
        print("🚀 Готов к деплою с постоянным хранением данных.")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Возможные причины:")
        print("1. MySQL сервис не запущен в Railway")
        print("2. Неправильные переменные подключения")
        print("3. Нет mysql-connector-python в requirements.txt")
        print("4. Проблемы с сетью до Railway")

if __name__ == "__main__":
    test_mysql_connection()
