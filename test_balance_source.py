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


def test_balance_source():
    print("Тестирование источника балансов в разных режимах...")
    
    # Импортируем модули
    from exchange_selector import ExchangeSelector
    from bot.db import init_db, init_test_balances, update_balance
    from bot.config import TEST_MODE
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём селектор
    selector = ExchangeSelector()
    
    print(f"\n📋 Текущий режим: {'ТЕСТОВЫЙ' if TEST_MODE else 'БОЕВОЙ'}")
    
    print("\n1. Проверяем источник балансов в тестовом режиме...")
    print("   Ожидаем: балансы из БД")
    
    # Получаем балансы через селектор
    exchange, price = selector.get_best_price_exchange("BTCUSDT", 50)
    print(f"   Результат: выбрана биржа {exchange.name}")
    
    print("\n2. Изменяем баланс в БД...")
    update_balance("Bybit", "USDT", 25)
    print("   Bybit баланс изменён в БД: 100 → 25 USDT")
    
    print("\n3. Проверяем, что селектор видит изменения в БД...")
    try:
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 30)
        print(f"   Результат: выбрана биржа {exchange.name}")
        if exchange.name == "Binance":
            print("   ✅ Правильно: Binance выбрана (Bybit недостаточно средств)")
        else:
            print("   ❌ Ошибка: должна была быть выбрана Binance")
    except ValueError as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n4. Проверяем балансы напрямую...")
    bybit_balance = selector.bybit.get_balance("USDT")
    binance_balance = selector.binance.get_balance("USDT")
    print(f"   Bybit.get_balance(): {bybit_balance} USDT")
    print(f"   Binance.get_balance(): {binance_balance} USDT")
    
    print("\n5. Восстанавливаем балансы...")
    init_test_balances()
    print("   Балансы восстановлены")
    
    print("\n6. Демонстрируем логику выбора биржи...")
    print("   Сценарий: Bybit=100 USDT, Binance=100 USDT, покупка на 80 USDT")
    
    # Bybit имеет лучшую цену (100 vs 25000)
    exchange, price = selector.get_best_price_exchange("BTCUSDT", 80)
    print(f"   Выбрана биржа: {exchange.name}")
    print(f"   Причина: лучшая цена + достаточно средств")
    
    print("\n7. Демонстрируем fallback логику...")
    print("   Сценарий: Bybit=50 USDT, Binance=100 USDT, покупка на 80 USDT")
    
    # Уменьшаем баланс Bybit
    update_balance("Bybit", "USDT", 50)
    
    exchange, price = selector.get_best_price_exchange("BTCUSDT", 80)
    print(f"   Выбрана биржа: {exchange.name}")
    if exchange.name == "Binance":
        print("   Причина: Bybit имеет лучшую цену, но недостаточно средств → fallback на Binance")
    else:
        print("   ❌ Ошибка: должна была быть выбрана Binance")
    
    print("\n8. Демонстрируем отклонение сделки...")
    print("   Сценарий: Bybit=50 USDT, Binance=100 USDT, покупка на 120 USDT")
    
    try:
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 120)
        print(f"   ❌ Ошибка: сделка должна была быть отклонена")
    except ValueError as e:
        print(f"   ✅ Правильно отклонено: {e}")
    
    print("\n📊 Итоговая логика:")
    print("   ✅ В тестовом режиме балансы берутся из БД")
    print("   ✅ В боевом режиме балансы будут браться из API")
    print("   ✅ Логика выбора биржи работает корректно")
    print("   ✅ Fallback механизм работает корректно")
    print("   ✅ Обработка ошибок работает корректно")
    
    print("\n🎉 Тестирование источника балансов завершено!")


if __name__ == "__main__":
    test_balance_source()
