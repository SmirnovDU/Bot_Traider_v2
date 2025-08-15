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


def test_exchange_selector():
    print("Тестирование выбора биржи по цене и балансам...")
    
    # Импортируем модули
    from exchange_selector import ExchangeSelector
    from bot.db import init_db, init_test_balances
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём селектор
    selector = ExchangeSelector()
    
    print("\n1. Тестируем получение лучшей цены с достаточными средствами...")
    exchange, price = selector.get_best_price_exchange("BTCUSDT", 50)
    print(f"Выбрана биржа: {exchange.name}")
    print(f"Цена: {price}")
    
    print("\n2. Тестируем получение биржи по имени...")
    bybit = selector.get_exchange_by_name("bybit")
    binance = selector.get_exchange_by_name("binance")
    print(f"Bybit: {bybit.name}")
    print(f"Binance: {binance.name}")
    
    print("\n3. Тестируем цены на обеих биржах...")
    bybit_price = bybit.get_last_price("BTCUSDT")
    binance_price = binance.get_last_price("BTCUSDT")
    print(f"Bybit цена BTC: {bybit_price}")
    print(f"Binance цена BTC: {binance_price}")
    
    print("\n4. Тестируем балансы на обеих биржах...")
    bybit_balance = bybit.get_balance("USDT")
    binance_balance = binance.get_balance("USDT")
    print(f"Bybit баланс USDT: {bybit_balance}")
    print(f"Binance баланс USDT: {binance_balance}")
    
    print("\n5. Тестируем выбор биржи с недостаточными средствами...")
    try:
        # Пытаемся купить на сумму больше баланса
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 200)
        print(f"❌ Ошибка: сделка должна была быть отклонена")
    except ValueError as e:
        print(f"✅ Правильно отклонено: {e}")
    
    print("\n6. Тестируем выбор биржи с достаточными средствами...")
    try:
        # Покупаем на сумму меньше баланса
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 10)
        print(f"✅ Успешно выбрана биржа: {exchange.name}")
        print(f"Цена: {price}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    if bybit_price <= binance_price:
        print("\n✅ Bybit имеет лучшую цену для покупки")
    else:
        print("\n✅ Binance имеет лучшую цену для покупки")
    
    print("\n🎉 Тестирование выбора биржи завершено!")


if __name__ == "__main__":
    test_exchange_selector()
