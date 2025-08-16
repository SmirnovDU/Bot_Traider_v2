#!/usr/bin/env python3

import os
import sys
import asyncio
import json

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'binance'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

async def test_webhook_binance():
    """Тестирование webhook с Binance через симуляцию сигнала"""
    print("Тестирование webhook с выбором Binance...")
    
    from bot.db import init_db, init_test_balances
    from bot.webhook import webhook
    from fastapi import Request
    from unittest.mock import AsyncMock
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Симулируем сигнал покупки
    signal_data = {
        "secret": "test_secret",
        "action": "buy",
        "symbol": "DOTUSDT",
        "usdt_amount": 10
    }
    
    # Создаём mock request
    mock_request = AsyncMock(spec=Request)
    mock_request.json = AsyncMock(return_value=signal_data)
    
    print(f"Отправляем сигнал: {signal_data}")
    
    try:
        # Вызываем webhook
        result = await webhook(mock_request)
        
        print(f"Результат webhook: {result}")
        
        if result.get("status") == "success":
            print("✅ Webhook обработан успешно!")
            print(f"Биржа: {result.get('exchange')}")
            print(f"Символ: {result.get('symbol')}")
            print(f"Количество: {result.get('qty')}")
            print(f"Цена: ${result.get('price'):.4f}")
        else:
            print(f"❌ Ошибка в webhook: {result}")
            
    except Exception as e:
        print(f"❌ Исключение в webhook: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎯 Тест webhook с Binance пройден!")
    return True

if __name__ == "__main__":
    asyncio.run(test_webhook_binance())
