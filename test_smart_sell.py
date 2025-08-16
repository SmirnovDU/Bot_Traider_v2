#!/usr/bin/env python3

import os
import sys
import asyncio

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

async def test_smart_sell():
    """Тестирование умной продажи - продает на той бирже где покупал"""
    print("Тестирование умной продажи...")
    
    from bot.db import init_db, init_test_balances, get_exchange_with_coins, get_unsold_quantity
    from bot.webhook import webhook
    from fastapi import Request
    from unittest.mock import AsyncMock
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Проверяем текущее состояние
    symbols = ["DOTUSDT", "ETHUSDT", "BTCUSDT"]
    
    print("📊 Анализ монет по биржам:")
    for symbol in symbols:
        bybit_qty = get_unsold_quantity("Bybit", symbol)
        binance_qty = get_unsold_quantity("Binance", symbol)
        exchange_with_coins = get_exchange_with_coins(symbol)
        
        print(f"  {symbol}:")
        print(f"    Bybit: {bybit_qty:.6f}")
        print(f"    Binance: {binance_qty:.6f}")
        print(f"    Максимум на: {exchange_with_coins}")
        print()
    
    # Тестируем продажу DOTUSDT (должно быть на Bybit)
    print("🔍 Тестируем продажу DOTUSDT:")
    
    # Сигнал продажи (без указания биржи)
    sell_signal = {
        "secret": "test_secret",
        "action": "sell",
        "symbol": "DOTUSDT",
        "usdt_amount": 10  # не используется для продаж
    }
    
    # Создаём mock request
    mock_request = AsyncMock(spec=Request)
    mock_request.json = AsyncMock(return_value=sell_signal)
    
    try:
        result = await webhook(mock_request)
        
        print(f"Результат продажи: {result}")
        
        if result.get("status") == "ok":
            exchange_used = result.get("exchange")
            print(f"✅ Продажа выполнена на бирже: {exchange_used}")
            
            # Проверяем что использована правильная биржа
            expected_exchange = get_exchange_with_coins("DOTUSDT")
            if exchange_used == expected_exchange:
                print(f"✅ Использована правильная биржа: {exchange_used}")
            else:
                print(f"❌ Ожидалась биржа {expected_exchange}, но использована {exchange_used}")
                
        elif result.get("status") == "Error":
            reason = result.get("reason")
            if reason == "No coins to sell":
                print("✅ Корректно: Нет монет для продажи")
            else:
                print(f"⚠️ Другая ошибка: {reason}")
        else:
            print(f"❌ Неожиданный результат: {result}")
            
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
        import traceback
        traceback.print_exc()
    
    # Тестируем продажу несуществующей монеты
    print("\n🔍 Тестируем продажу несуществующей монеты:")
    
    fake_sell_signal = {
        "secret": "test_secret", 
        "action": "sell",
        "symbol": "FAKEUSDT",
        "usdt_amount": 10
    }
    
    mock_request.json = AsyncMock(return_value=fake_sell_signal)
    
    try:
        result = await webhook(mock_request)
        print(f"Результат: {result}")
        
        if result.get("reason") == "No coins to sell":
            print("✅ Корректно: Нет монет для продажи несуществующей пары")
        else:
            print(f"⚠️ Неожиданный результат: {result}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_smart_sell())
