#!/usr/bin/env python3

import os
import sys

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

def test_persistence():
    """Тестирование сохранения данных при повторной инициализации"""
    print("Тестирование сохранения данных БД при деплое...")
    
    from bot.db import init_db, init_test_balances, save_trade, get_all_balances, get_trades_summary
    from bot.exchanges.bybit import BybitExchange
    from datetime import datetime, timezone
    
    # === ПЕРВАЯ ИНИЦИАЛИЗАЦИЯ ===
    print("\n1️⃣ Первая инициализация (имитация первого деплоя):")
    init_db()
    init_test_balances()
    
    # Показываем начальные балансы
    balances = get_all_balances()
    print("📊 Начальные балансы:")
    for balance in balances:
        print(f"  {balance['exchange']} - {balance['coin']}: {balance['amount']}")
    
    # Симулируем покупку
    print("\n💰 Симулируем покупку DOTUSDT...")
    bybit = BybitExchange()
    
    # Покупаем
    symbol = "DOTUSDT"
    usdt_amount = 10
    price = bybit.get_last_price(symbol)
    qty = usdt_amount / price
    
    result = bybit.place_order("buy", symbol, qty, "quoteCoin")
    
    # Сохраняем сделку в БД
    import time
    unique_id = f"test_{int(time.time())}_DOTUSDT_BUY"
    trade_data = {
        "request_id": unique_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exchange": "Bybit",
        "side": "buy",
        "symbol": symbol,
        "price": price,
        "qty": qty,
        "amount_usdt": usdt_amount,
        "fee": result['fee'],
        "profit": 0.0,
        "balance_after": bybit.get_balance("USDT"),
        "note": "Тест сохранения данных"
    }
    save_trade(trade_data)
    
    print(f"✅ Покупка выполнена: {qty:.6f} DOT по ${price:.4f}")
    print(f"💰 Баланс USDT: {bybit.get_balance('USDT')}")
    print(f"🪙 Баланс DOT: {bybit.get_balance('DOT')}")
    
    # Показываем статистику
    trades = get_trades_summary()
    print(f"📜 Сделок в БД: {trades['total_trades']}")
    
    # === ВТОРАЯ ИНИЦИАЛИЗАЦИЯ (ИМИТАЦИЯ ДЕПЛОЯ) ===
    print("\n2️⃣ Повторная инициализация (имитация повторного деплоя):")
    init_db()
    init_test_balances()
    
    # Проверяем что данные сохранились
    bybit2 = BybitExchange()
    balances_after = get_all_balances()
    trades_after = get_trades_summary()
    
    print("📊 Балансы после повторной инициализации:")
    for balance in balances_after:
        print(f"  {balance['exchange']} - {balance['coin']}: {balance['amount']}")
    
    print(f"🪙 DOT баланс: {bybit2.get_balance('DOT')}")
    print(f"📜 Сделок в БД: {trades_after['total_trades']}")
    
    # === ПРОВЕРКА РЕЗУЛЬТАТОВ ===
    print("\n✅ РЕЗУЛЬТАТЫ ТЕСТА:")
    
    # Проверяем что DOT баланс сохранился
    dot_balance = bybit2.get_balance('DOT')
    if dot_balance > 0:
        print(f"✅ DOT баланс сохранился: {dot_balance:.6f}")
    else:
        print(f"❌ DOT баланс потерян!")
    
    # Проверяем что USDT баланс сохранился (должен быть меньше 1000)
    usdt_balance = bybit2.get_balance('USDT')
    if usdt_balance < 1000:
        print(f"✅ USDT баланс сохранился: {usdt_balance} (потрачено на покупку)")
    else:
        print(f"❌ USDT баланс сброшен до {usdt_balance}!")
    
    # Проверяем что сделки сохранились
    if trades_after['total_trades'] > 0:
        print(f"✅ Сделки сохранились: {trades_after['total_trades']}")
        if trades_after['recent_trades']:
            recent = trades_after['recent_trades'][0]
            print(f"   Последняя: {recent['side']} {recent['symbol']} на ${recent['amount_usdt']}")
    else:
        print(f"❌ Сделки потеряны!")
    
    print(f"\n🎯 ВЫВОД: {'Данные сохраняются корректно!' if dot_balance > 0 and trades_after['total_trades'] > 0 else 'Есть проблемы с сохранением данных!'}")

if __name__ == "__main__":
    test_persistence()
