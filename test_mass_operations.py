#!/usr/bin/env python3
"""
Тест массовых операций продажи монет
"""

import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from bot.mass_operations import sell_all_coins, sell_all_binance, sell_all_bybit
from bot.db import get_all_balances


async def test_mass_operations():
    """Тестируем массовые операции"""
    
    print("🧪 Тестирование массовых операций")
    print("=" * 50)
    
    # Проверяем текущие балансы
    print("\n📊 Текущие балансы:")
    balances = get_all_balances()
    if balances:
        for balance in balances:
            print(f"• {balance['exchange']}: {balance['amount']} {balance['coin']}")
    else:
        print("Нет активных балансов")
    
    print("\n" + "=" * 50)
    
    # Тест 1: Продажа всех монет на Binance
    print("\n🔄 Тест 1: Продажа всех монет на Binance")
    result = await sell_all_binance()
    print(f"Результат: {result}")
    
    print("\n" + "=" * 50)
    
    # Тест 2: Продажа всех монет на Bybit
    print("\n🔄 Тест 2: Продажа всех монет на Bybit")
    result = await sell_all_bybit()
    print(f"Результат: {result}")
    
    print("\n" + "=" * 50)
    
    # Тест 3: Продажа всех монет на всех биржах
    print("\n🔄 Тест 3: Продажа всех монет на всех биржах")
    result = await sell_all_coins()
    print(f"Результат: {result}")
    
    print("\n" + "=" * 50)
    
    # Проверяем балансы после операций
    print("\n📊 Балансы после операций:")
    balances = get_all_balances()
    if balances:
        for balance in balances:
            print(f"• {balance['exchange']}: {balance['amount']} {balance['coin']}")
    else:
        print("Нет активных балансов")


async def test_single_operation():
    """Тестируем одну операцию"""
    
    print("🧪 Тестирование одной операции продажи")
    print("=" * 50)
    
    # Проверяем текущие балансы
    print("\n📊 Текущие балансы:")
    balances = get_all_balances()
    if balances:
        for balance in balances:
            print(f"• {balance['exchange']}: {balance['amount']} {balance['coin']}")
    else:
        print("Нет активных балансов")
        return
    
    # Выбираем первую монету для продажи (не USDT)
    coin_to_sell = None
    for balance in balances:
        if balance['coin'] != 'USDT' and balance['amount'] > 0:
            coin_to_sell = balance
            break
    
    if not coin_to_sell:
        print("Нет монет для продажи (только USDT)")
        return
    
    print(f"\n🔄 Продаём {coin_to_sell['amount']} {coin_to_sell['coin']} на {coin_to_sell['exchange']}")
    
    # Продаём только на одной бирже
    if coin_to_sell['exchange'].lower() == 'binance':
        result = await sell_all_binance()
    else:
        result = await sell_all_bybit()
    
    print(f"Результат: {result}")


if __name__ == "__main__":
    print("🚀 Запуск тестов массовых операций")
    print("⚠️  ВНИМАНИЕ: Это реальные операции продажи!")
    
    choice = input("\nВыберите тест:\n1. Тест всех операций\n2. Тест одной операции\n3. Выход\nВаш выбор: ")
    
    if choice == "1":
        asyncio.run(test_mass_operations())
    elif choice == "2":
        asyncio.run(test_single_operation())
    else:
        print("Выход из программы")
