#!/usr/bin/env python3

"""
Демонстрация торгового бота для TradingView - Версия 3.0
Обновлённая версия с выбором биржи по цене и балансам
"""

import os
import sys

# Устанавливаем переменные окружения для демо
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'demo_secret_123'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

def demo_v3():
    print("🚀 ДЕМОНСТРАЦИЯ ТОРГОВОГО БОТА ДЛЯ TRADINGVIEW - ВЕРСИЯ 3.0")
    print("=" * 60)
    print("✨ НОВЫЕ ВОЗМОЖНОСТИ:")
    print("  • Выбор биржи по лучшей цене")
    print("  • Проверка достаточности средств")
    print("  • Автоматический fallback на вторую биржу")
    print("  • Новый расчёт комиссий на основе балансов")
    print("=" * 60)
    
    # Импортируем модули
    from bot.main import app
    from bot.db import init_db, init_test_balances, update_balance
    from bot.exchange_selector import ExchangeSelector
    from fastapi.testclient import TestClient
    
    print("\n📋 Инициализация...")
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
    
    # Демонстрируем выбор биржи по цене и балансам
    print("\n🔍 ДЕМО: Выбор биржи по лучшей цене и балансам")
    print("-" * 50)
    
    selector = ExchangeSelector()
    exchange, price = selector.get_best_price_exchange("BTCUSDT", 100)
    print(f"Для покупки BTC на 100 USDT выбрана биржа: {exchange.name}")
    print(f"Цена: {price} USDT")
    
    # Демонстрируем сценарий с недостаточными средствами
    print("\n⚠️  ДЕМО: Сценарий с недостаточными средствами")
    print("-" * 50)
    
    print("1. Уменьшаем баланс на Bybit до 50 USDT...")
    update_balance("Bybit", "USDT", 50)
    
    print("2. Пытаемся купить на 80 USDT...")
    try:
        exchange, price = selector.get_best_price_exchange("BTCUSDT", 80)
        print(f"✅ Выбрана биржа: {exchange.name}")
        print(f"Цена: {price} USDT")
        if exchange.name == "Binance":
            print("✅ Правильно: Binance выбрана как fallback")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    print("3. Восстанавливаем балансы...")
    init_test_balances()
    
    # Демонстрируем покупку с автоматическим выбором биржи
    print("\n🟢 ДЕМО: Покупка BTC с выбором лучшей цены")
    print("-" * 50)
    
    buy_data = {
        "secret": "demo_secret_123",
        "action": "buy",
        "symbol": "BTCUSDT",
        "usdt_amount": 100
    }
    
    print(f"Отправляем сигнал покупки: {buy_data}")
    response = client.post("/webhook", json=buy_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Покупка выполнена!")
        print(f"  Выбранная биржа: {result['exchange']}")
        print(f"  Request ID: {result['request_id']}")
        print(f"  Баланс после: {result['balance_after']} USDT")
        print(f"  Комиссия: {result['order']['fee']} USDT")
    else:
        print(f"❌ Ошибка: {response.json()}")
    
    # Показываем обновлённые балансы
    print("\n💰 Балансы после покупки:")
    response = client.get("/balances")
    balances = response.json()["balances"]
    for balance in balances:
        print(f"  {balance[0]}: {balance[2]} {balance[1]}")
    
    # Демонстрируем продажу
    print("\n🔴 ДЕМО: Продажа BTC")
    print("-" * 50)
    
    sell_data = {
        "secret": "demo_secret_123",
        "action": "sell",
        "symbol": "BTCUSDT"
    }
    
    print(f"Отправляем сигнал продажи: {sell_data}")
    response = client.post("/webhook", json=sell_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Продажа выполнена!")
        print(f"  Request ID: {result['request_id']}")
        print(f"  Баланс после: {result['balance_after']} USDT")
        if result.get('profit') is not None:
            print(f"  Прибыль: {result['profit']} USDT")
    else:
        print(f"❌ Ошибка: {response.json()}")
    
    # Финальные балансы
    print("\n💰 Финальные балансы:")
    response = client.get("/balances")
    balances = response.json()["balances"]
    for balance in balances:
        print(f"  {balance[0]}: {balance[2]} {balance[1]}")
    
    # Демонстрируем проверку лимитов
    print("\n⚠️  ДЕМО: Проверка лимитов")
    print("-" * 50)
    
    large_buy_data = {
        "secret": "demo_secret_123",
        "action": "buy",
        "symbol": "ETHUSDT",
        "usdt_amount": 500,  # 50% от баланса - превышает лимит 10%
    }
    
    print(f"Пытаемся купить на {large_buy_data['usdt_amount']} USDT (50% от баланса)")
    response = client.post("/webhook", json=large_buy_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'Error':
            print(f"✅ Лимит сработал: {result['reason']}")
            print(f"  Максимальная сумма: {result['max_amount']} USDT")
        else:
            print(f"❌ Лимит не сработал!")
    else:
        print(f"❌ Ошибка: {response.json()}")
    
    # Показываем статистику
    print("\n📊 СТАТИСТИКА")
    print("-" * 50)
    
    import sqlite3
    conn = sqlite3.connect('bot/trades.db')
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM trades")
    total_trades = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(profit) FROM trades WHERE profit IS NOT NULL")
    total_profit = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(*) FROM trades WHERE side='buy'")
    buy_trades = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM trades WHERE side='sell'")
    sell_trades = cur.fetchone()[0]
    
    cur.execute("SELECT exchange, COUNT(*) FROM trades GROUP BY exchange")
    trades_by_exchange = cur.fetchall()
    
    conn.close()
    
    print(f"Всего сделок: {total_trades}")
    print(f"Покупок: {buy_trades}")
    print(f"Продаж: {sell_trades}")
    print(f"Общая прибыль: {total_profit:.2f} USDT")
    
    print("\nСделки по биржам:")
    for exchange, count in trades_by_exchange:
        print(f"  {exchange}: {count} сделок")
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ВЕРСИИ 3.0 ЗАВЕРШЕНА!")
    print("\n📝 Новые возможности:")
    print("  ✅ Автоматический выбор биржи по лучшей цене")
    print("  ✅ Проверка достаточности средств")
    print("  ✅ Fallback на вторую биржу при недостатке средств")
    print("  ✅ Новый расчёт комиссий на основе балансов")
    print("  ✅ Улучшенная логика покупки/продажи")
    print("  ✅ Более точный расчёт прибыли")


if __name__ == "__main__":
    demo_v3()
