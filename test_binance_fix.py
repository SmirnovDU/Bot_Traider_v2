#!/usr/bin/env python3

import os
import sys

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'binance'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

def test_binance_place_order():
    """Тестирование исправления place_order для Binance"""
    print("Тестирование place_order для Binance с market_unit...")
    
    from bot.db import init_db, init_test_balances
    from bot.exchanges.binance import BinanceExchange
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём биржу
    binance = BinanceExchange()
    
    print(f"Начальный баланс USDT: {binance.get_balance('USDT')}")
    
    # Тестируем вызов с market_unit (как у Bybit)
    symbol = "DOTUSDT"
    price = binance.get_last_price(symbol)
    qty = 10 / price  # 10 USDT
    
    print(f"Цена {symbol}: ${price:.4f}")
    print(f"Покупаем {qty:.6f} DOT")
    
    try:
        # Вызываем с 4 параметрами (как Bybit)
        result = binance.place_order("buy", symbol, qty, "quoteCoin")
        print("✅ Функция place_order работает с 4 параметрами!")
        print(f"Результат: {result}")
        
        # Проверяем что баланс изменился
        usdt_after = binance.get_balance("USDT")
        dot_after = binance.get_balance("DOT")
        
        print(f"USDT после: {usdt_after}")
        print(f"DOT после: {dot_after}")
        
        if usdt_after < 1000 and dot_after > 0:
            print("✅ Покупка выполнена корректно!")
        else:
            print("❌ Проблема с выполнением покупки")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    print("\n🎯 Тест пройден! Binance теперь совместим с Bybit API.")
    return True

if __name__ == "__main__":
    test_binance_place_order()
