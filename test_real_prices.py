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

def test_real_prices():
    print("Тестирование реальных цен и правильных комиссий...")
    
    # Импортируем модули
    from bot.db import init_db, init_test_balances
    from bot.exchanges.bybit import BybitExchange
    from bot.exchanges.binance import BinanceExchange
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём биржи
    bybit = BybitExchange()
    binance = BinanceExchange()
    
    print(f"Начальный баланс USDT: {bybit.get_balance('USDT')}")
    
    # Тестируем получение реальных цен
    symbols = ["DOTUSDT", "BTCUSDT", "ETHUSDT"]
    
    for symbol in symbols:
        print(f"\n📊 Тестируем {symbol}:")
        
        bybit_price = bybit.get_last_price(symbol)
        binance_price = binance.get_last_price(symbol)
        
        print(f"  Bybit цена: ${bybit_price:.6f}")
        print(f"  Binance цена: ${binance_price:.6f}")
        
        # Проверяем что цены разумные
        if bybit_price > 0 and bybit_price != 100.0:
            print(f"  ✅ Bybit: реальная цена получена")
        else:
            print(f"  ⚠️ Bybit: используется резервная цена")
            
        if binance_price > 0 and binance_price != 25000.0:
            print(f"  ✅ Binance: реальная цена получена")
        else:
            print(f"  ⚠️ Binance: используется резервная цена")
    
    # Тестируем покупку с правильной комиссией
    print(f"\n🛒 Тестируем покупку DOTUSDT...")
    
    symbol = "DOTUSDT"
    usdt_amount = 10
    
    # Получаем балансы ДО
    usdt_before = bybit.get_balance("USDT")
    dot_before = bybit.get_balance("DOT")
    
    print(f"  USDT до покупки: {usdt_before}")
    print(f"  DOT до покупки: {dot_before}")
    
    # Покупаем
    price = bybit.get_last_price(symbol)
    qty = usdt_amount / price
    
    result = bybit.place_order("buy", symbol, qty, "quoteCoin")
    
    # Получаем балансы ПОСЛЕ
    usdt_after = bybit.get_balance("USDT")
    dot_after = bybit.get_balance("DOT")
    
    print(f"  USDT после покупки: {usdt_after}")
    print(f"  DOT после покупки: {dot_after}")
    print(f"  Цена: ${price:.6f}")
    print(f"  Количество: {qty:.6f}")
    print(f"  Комиссия: ${result['fee']:.4f}")
    
    # Проверяем что комиссия разумная (не -980!)
    if abs(result['fee']) < 1.0:  # Комиссия должна быть меньше $1
        print(f"  ✅ Комиссия рассчитана корректно")
    else:
        print(f"  ❌ Комиссия выглядит неправильно: ${result['fee']:.4f}")
    
    # Проверяем что цена не $100
    if price != 100.0:
        print(f"  ✅ Используется реальная цена")
    else:
        print(f"  ⚠️ Используется резервная цена $100")

if __name__ == "__main__":
    test_real_prices()
