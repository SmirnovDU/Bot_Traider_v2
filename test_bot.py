#!/usr/bin/env python3

import os
import sys
import requests
import json
import time

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '100'

# Добавляем путь к модулям
sys.path.append('bot')

def test_bot():
    print("Тестирование торгового бота...")
    
    # Импортируем модули
    try:
        from bot.main import app
        from bot.db import init_db, init_test_balances
        from bot.exchanges.bybit import BybitExchange
        from bot.exchanges.binance import BinanceExchange
        
        print("✓ Модули импортированы успешно")
        
        # Инициализируем БД
        init_db()
        init_test_balances()
        print("✓ База данных инициализирована")
        
        # Тестируем биржи
        bybit = BybitExchange()
        binance = BinanceExchange()
        
        print(f"✓ Bybit: {bybit.name}")
        print(f"✓ Binance: {binance.name}")
        
        # Тестируем получение цены
        price = bybit.get_last_price("BTCUSDT")
        print(f"✓ Цена BTC: {price}")
        
        # Тестируем баланс
        balance = bybit.get_balance("USDT")
        print(f"✓ Баланс USDT: {balance}")
        
        print("\n🎉 Все тесты пройдены успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bot()
