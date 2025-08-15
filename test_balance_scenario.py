#!/usr/bin/env python3

import os
import sys

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '100'

# Добавляем путь к модулям
sys.path.append('bot')


def test_balance_scenario():
    print("Тестирование сценария с недостаточными средствами...")
    
    # Импортируем модули
    from exchange_selector import ExchangeSelector
    from bot.db import init_db, init_test_balances, update_balance
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём селектор
    selector = ExchangeSelector()
    
    print("\n1. Начальное состояние:")
    bybit_balance = selector.bybit.get_balance("USDT")
    binance_balance = selector.binance.get_balance("USDT")
    print(f"Bybit баланс: {bybit_balance} USDT")
    print(f"Binance баланс: {binance_balance} USDT")
    
    print("\n2. Симулируем недостаток средств на Bybit...")
    # Уменьшаем баланс на Bybit
    update_balance("Bybit", "USDT", 50)
    bybit_balance = selector.bybit.get_balance("USDT")
    print(f"Bybit баланс после изменения: {bybit_balance} USDT")
    
    print("\n3. Тестируем покупку на 80 USDT (недостаточно на Bybit, достаточно на Binance)...")
    try:
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 80)
        print(f"✅ Успешно выбрана биржа: {exchange.name}")
        print(f"Цена: {price}")
        
        if exchange.name == "Binance":
            print("✅ Правильно выбрана Binance (на Bybit недостаточно средств)")
        else:
            print("❌ Ошибка: должна была быть выбрана Binance")
            
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n4. Тестируем покупку на 30 USDT (достаточно на обеих биржах)...")
    try:
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 30)
        print(f"✅ Успешно выбрана биржа: {exchange.name}")
        print(f"Цена: {price}")
        
        if exchange.name == "Bybit":
            print("✅ Правильно выбрана Bybit (лучшая цена)")
        else:
            print("❌ Ошибка: должна была быть выбрана Bybit")
            
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n5. Тестируем покупку на 120 USDT (недостаточно на обеих биржах)...")
    try:
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 120)
        print(f"❌ Ошибка: сделка должна была быть отклонена")
    except ValueError as e:
        print(f"✅ Правильно отклонено: {e}")
    
    print("\n6. Восстанавливаем балансы...")
    init_test_balances()
    bybit_balance = selector.bybit.get_balance("USDT")
    binance_balance = selector.binance.get_balance("USDT")
    print(f"Bybit баланс восстановлен: {bybit_balance} USDT")
    print(f"Binance баланс восстановлен: {binance_balance} USDT")
    
    print("\n🎉 Тестирование сценария завершено!")


if __name__ == "__main__":
    test_balance_scenario()
