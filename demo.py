#!/usr/bin/env python3

"""
Демонстрация торгового бота для TradingView
Версия 1.0 - Полная функциональность
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

def demo():
    print("🚀 ДЕМОНСТРАЦИЯ ТОРГОВОГО БОТА ДЛЯ TRADINGVIEW")
    print("=" * 50)
    
    # Импортируем модули
    from bot.main import app
    from bot.db import init_db, init_test_balances, get_all_balances
    from bot.exchanges.bybit import BybitExchange
    from bot.exchanges.binance import BinanceExchange
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
    
    # Демонстрируем покупку
    print("\n🟢 ДЕМО: Покупка BTC")
    print("-" * 30)
    
    buy_data = {
        "secret": "demo_secret_123",
        "action": "buy",
        "symbol": "BTCUSDT",
        "usdt_amount": 100,
        "exchange": "bybit"
    }
    
    print(f"Отправляем сигнал: {buy_data}")
    response = client.post("/webhook", json=buy_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Покупка выполнена!")
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
    print("-" * 30)
    
    sell_data = {
        "secret": "demo_secret_123",
        "action": "sell",
        "symbol": "BTCUSDT",
        "exchange": "bybit"
    }
    
    print(f"Отправляем сигнал: {sell_data}")
    response = client.post("/webhook", json=sell_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Продажа выполнена!")
        print(f"  Request ID: {result['request_id']}")
        print(f"  Баланс после: {result['balance_after']} USDT")
        if result.get('profit'):
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
    print("-" * 30)
    
    large_buy_data = {
        "secret": "demo_secret_123",
        "action": "buy",
        "symbol": "ETHUSDT",
        "usdt_amount": 500,  # 50% от баланса - превышает лимит 10%
        "exchange": "bybit"
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
    print("-" * 30)
    
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
    
    conn.close()
    
    print(f"Всего сделок: {total_trades}")
    print(f"Покупок: {buy_trades}")
    print(f"Продаж: {sell_trades}")
    print(f"Общая прибыль: {total_profit:.2f} USDT")
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("\n📝 Возможности бота:")
    print("  ✅ Поддержка Bybit и Binance")
    print("  ✅ Тестовый и боевой режимы")
    print("  ✅ Ограничение позиций 10%")
    print("  ✅ Учёт комиссий")
    print("  ✅ Уникальные request_id")
    print("  ✅ Расчёт прибыли")
    print("  ✅ Логирование в SQLite")
    print("  ✅ Webhook для TradingView")
    print("  ✅ Безопасность и валидация")


if __name__ == "__main__":
    demo()
