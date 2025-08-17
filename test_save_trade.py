#!/usr/bin/env python3
"""
Тест сохранения сделок в БД
"""

import os
import sys
import time
from datetime import datetime, timezone

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

from bot.config import *
from bot.db import init_db, save_trade, get_trades_summary
from bot.utils import generate_request_id

def test_save_trade():
    """Тест сохранения сделки в БД"""
    print("🧪 Тест сохранения сделок в БД")
    
    # Инициализируем БД
    init_db()
    
    # Получаем статистику до сохранения
    summary_before = get_trades_summary()
    trades_before = summary_before['total_trades']
    print(f"\n1. Количество сделок до теста: {trades_before}")
    
    # Создаем тестовую сделку
    request_id = generate_request_id("TESTUSDT", "buy")
    trade_data = {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exchange": "Bybit",
        "side": "buy",
        "symbol": "TESTUSDT",
        "price": 1.0,
        "qty": 10.0,
        "amount_usdt": 10.0,
        "fee": 0.01,
        "profit": None,
        "profit_no_fees": None,
        "balance_after": 990.0,
        "note": "Test trade"
    }
    
    print(f"\n2. Сохраняем тестовую сделку: {request_id}")
    
    # Сохраняем сделку
    try:
        save_trade(trade_data)
        print("   ✅ Сделка сохранена без ошибок")
    except Exception as e:
        print(f"   ❌ Ошибка сохранения: {e}")
        return False
    
    # Проверяем что сделка появилась в БД
    summary_after = get_trades_summary()
    trades_after = summary_after['total_trades']
    print(f"\n3. Количество сделок после теста: {trades_after}")
    
    if trades_after > trades_before:
        print("   ✅ Сделка успешно сохранена в БД")
        
        # Проверяем что это наша сделка
        recent_trades = summary_after['recent_trades']
        if recent_trades and recent_trades[0]['symbol'] == 'TESTUSDT':
            print("   ✅ Сохраненная сделка найдена в списке")
            print(f"   Детали: {recent_trades[0]}")
        else:
            print("   ⚠️ Сделка не найдена в списке последних")
    else:
        print("   ❌ Сделка НЕ сохранилась в БД")
        return False
    
    print("\n🎉 Тест пройден успешно!")
    return True

if __name__ == "__main__":
    test_save_trade()
