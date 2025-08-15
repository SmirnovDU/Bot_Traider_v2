#!/usr/bin/env python3

"""
Демонстрация торгового бота для TradingView - Версия 2.0
Обновлённая версия с новым расчётом комиссий и выбором биржи по цене
"""

import os
import sys
import time

# Устанавливаем переменные окружения для демо
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'demo_secret_123'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

def demo_v2():
    print("🚀 ДЕМОНСТРАЦИЯ ТОРГОВОГО БОТА ДЛЯ TRADINGVIEW - ВЕРСИЯ 2.0")
    print("=" * 60)
    print("✨ НОВЫЕ ВОЗМОЖНОСТИ:")
    print("  • Выбор биржи по лучшей цене для покупки")
    print("  • Новый расчёт комиссий на основе балансов")
    print("  • Единый баланс для обеих бирж в тестовом режиме")
    print("=" * 60)
    
    # Импортируем модули
    from bot.main import app
    from bot.db import init_db, init_test_balances, get_all_balances
    from bot.exchanges.bybit import BybitExchange
    from bot.exchanges.binance import BinanceExchange
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
    
    # Демонстрируем выбор биржи по цене
    print("\n🔍 ДЕМО: Выбор биржи по лучшей цене")
    print("-" * 40)
    
    selector = ExchangeSelector()
    exchange, price = selector.get_best_price_exchange("BTCUSDT")
    print(f"Для покупки BTC выбрана биржа: {exchange.name}")
    print(f"Цена: {price} USDT")
    
    # Демонстрируем покупку с автоматическим выбором биржи
    print("\n🟢 ДЕМО: Покупка BTC с выбором лучшей цены")
    print("-" * 40)
    
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
    print("-" * 40)
    
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
    print("-" * 40)
    
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
    print("-" * 40)
    
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
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ВЕРСИИ 2.0 ЗАВЕРШЕНА!")
    print("\n📝 Новые возможности:")
    print("  ✅ Автоматический выбор биржи по лучшей цене")
    print("  ✅ Новый расчёт комиссий на основе балансов")
    print("  ✅ Единый баланс для обеих бирж в тестовом режиме")
    print("  ✅ Улучшенная логика покупки/продажи")
    print("  ✅ Более точный расчёт прибыли")


if __name__ == "__main__":
    demo_v2()
