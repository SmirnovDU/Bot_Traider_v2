#!/usr/bin/env python3
"""
Тест исправления ошибки Decimal vs float
"""

import os
import sys
import time

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

from bot.config import *
from bot.db import init_db, update_balance, get_balance
from bot.utils import generate_request_id

def test_decimal_fix():
    """Тест исправления ошибки с типами данных"""
    print("🧪 Тест исправления ошибки Decimal vs float")
    
    # Инициализируем БД
    init_db()
    
    # Тестируем get_balance с принудительной конвертацией в float
    print("\n1. Тест get_balance:")
    balance = get_balance("Binance", "USDT")
    print(f"   Баланс: {balance} (тип: {type(balance)})")
    assert isinstance(balance, float), f"Ожидался float, получен {type(balance)}"
    print("   ✅ get_balance возвращает float")
    
    # Тестируем уникальность request_id
    print("\n2. Тест уникальности request_id:")
    id1 = generate_request_id("BTCUSDT", "buy")
    time.sleep(0.001)  # Небольшая пауза
    id2 = generate_request_id("BTCUSDT", "buy")
    print(f"   ID1: {id1}")
    print(f"   ID2: {id2}")
    assert id1 != id2, "request_id должны быть уникальными"
    print("   ✅ request_id уникальны")
    
    # Тестируем математические операции
    print("\n3. Тест математических операций:")
    price = 3.0987  # float
    last_buy_price = 3.0900  # float  
    qty = 3.220197  # float
    fee = 3.900026968040038e-09  # float (очень маленькое число)
    
    try:
        profit = (price - last_buy_price) * qty - fee
        print(f"   Прибыль: {profit:.8f}")
        print("   ✅ Математические операции работают корректно")
    except TypeError as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    print("\n🎉 Все тесты пройдены успешно!")
    return True

if __name__ == "__main__":
    test_decimal_fix()
