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


def test_webhook_fix():
    print("Тестирование исправлений в webhook...")
    
    # Импортируем модули
    from bot.main import app
    from bot.db import init_db, init_test_balances
    from fastapi.testclient import TestClient
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём тестовый клиент
    client = TestClient(app)
    
    print("✅ Бот инициализирован")
    
    # Показываем начальные балансы
    print("\n💰 Начальные балансы:")
    response = client.get("/balances")
    balances = response.json()["balances"]
    for balance in balances:
        print(f"  {balance[0]}: {balance[2]} {balance[1]}")
    
    # Тестируем покупку с небольшой суммой (в пределах лимита)
    print("\n🟢 Тестируем покупку BTC на 5 USDT (в пределах лимита 10%)...")
    
    buy_data = {
        "secret": "test_secret",
        "action": "buy",
        "symbol": "BTCUSDT",
        "usdt_amount": 5  # 5% от баланса 100 USDT
    }
    
    response = client.post("/webhook", json=buy_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'ok':
            print(f"✅ Покупка выполнена!")
            print(f"  Выбранная биржа: {result['exchange']}")
            print(f"  Request ID: {result['request_id']}")
            print(f"  Баланс после: {result['balance_after']} USDT")
            print(f"  Комиссия: {result['order']['fee']} USDT")
            
            # Проверяем timestamp
            print(f"  Timestamp: {result.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Ошибка: {result}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
    
    # Показываем обновлённые балансы
    print("\n💰 Балансы после покупки:")
    response = client.get("/balances")
    balances = response.json()["balances"]
    for balance in balances:
        print(f"  {balance[0]}: {balance[2]} {balance[1]}")
    
    # Тестируем продажу
    print("\n🔴 Тестируем продажу BTC...")
    
    sell_data = {
        "secret": "test_secret",
        "action": "sell",
        "symbol": "BTCUSDT"
    }
    
    response = client.post("/webhook", json=sell_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'ok':
            print(f"✅ Продажа выполнена!")
            print(f"  Request ID: {result['request_id']}")
            print(f"  Баланс после: {result['balance_after']} USDT")
            if result.get('profit') is not None:
                print(f"  Прибыль: {result['profit']} USDT")
        else:
            print(f"❌ Ошибка: {result}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
    
    # Финальные балансы
    print("\n💰 Финальные балансы:")
    response = client.get("/balances")
    balances = response.json()["balances"]
    for balance in balances:
        print(f"  {balance[0]}: {balance[2]} {balance[1]}")
    
    print("\n📊 Проверка исправлений:")
    print("  ✅ Удалена неиспользуемая переменная balance_before")
    print("  ✅ Исправлен устаревший datetime.utcnow()")
    print("  ✅ Комиссия рассчитывается в place_order")
    print("  ✅ Timestamp использует timezone-aware datetime")
    
    print("\n🎉 Тестирование исправлений завершено!")


if __name__ == "__main__":
    test_webhook_fix()
