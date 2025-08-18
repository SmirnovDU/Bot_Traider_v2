#!/usr/bin/env python3
"""
Тест массовых операций в ТЕСТОВОМ режиме
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.mass_operations import sell_all_coins
from bot.db import get_all_balances, init_test_balances


async def test_mass_operations():
    """Тестируем массовые операции в тестовом режиме"""
    
    print("🧪 Тестирование массовых операций в ТЕСТОВОМ режиме")
    print("=" * 50)
    
    # Инициализируем тестовые балансы
    print("\n📊 Инициализация тестовых балансов...")
    init_test_balances()
    
    # Проверяем текущие балансы
    print("\n📊 Текущие балансы:")
    balances = get_all_balances()
    if balances:
        for balance in balances:
            print(f"• {balance['exchange']}: {balance['amount']} {balance['coin']}")
    
    print("\n" + "=" * 50)
    
    # Тест: Продажа всех монет
    print("\n🔄 Тест: Продажа всех монет (ТЕСТОВЫЙ РЕЖИМ)")
    result = await sell_all_coins()
    print(f"Результат: {result}")
    
    print("\n" + "=" * 50)
    
    # Финальная проверка балансов
    print("\n📊 Финальные балансы:")
    balances = get_all_balances()
    if balances:
        for balance in balances:
            print(f"• {balance['exchange']}: {balance['amount']} {balance['coin']}")
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    print("🚀 Запуск тестов массовых операций в ТЕСТОВОМ режиме")
    print("🧪 ВНИМАНИЕ: Это тестовые операции без реальных запросов к биржам!")
    
    asyncio.run(test_mass_operations())
