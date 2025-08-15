#!/usr/bin/env python3

import os
import sys
import sqlite3

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '100'

# Добавляем путь к модулям
sys.path.append('bot')

def test_detailed():
    print("Детальное тестирование бота...")
    
    # Импортируем модули
    from bot.db import init_db, init_test_balances, save_trade, get_balance
    from bot.exchanges.bybit import BybitExchange
    from bot.utils import generate_request_id, calculate_qty_by_precision, calculate_fee
    from datetime import datetime
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём экземпляр биржи
    bybit = BybitExchange()
    
    print(f"Начальный баланс USDT: {bybit.get_balance('USDT')}")
    
    # Симулируем покупку
    symbol = "BTCUSDT"
    usdt_amount = 10
    price = bybit.get_last_price(symbol)
    qty = calculate_qty_by_precision(usdt_amount, price, 6)
    fee = calculate_fee(qty * price, bybit.fee_percent)
    
    print(f"Покупаем {qty} {symbol} по цене {price}")
    print(f"Комиссия: {fee}")
    
    # Выполняем покупку
    result = bybit.place_order("buy", symbol, qty, "quoteCoin")
    print(f"Результат покупки: {result}")
    
    # Получаем обновлённый баланс
    balance_after = bybit.get_balance("USDT")
    print(f"Баланс после покупки: {balance_after}")
    
    # Сохраняем сделку в БД
    trade_data = {
        "request_id": generate_request_id(symbol, "buy"),
        "timestamp": datetime.utcnow().isoformat(),
        "exchange": bybit.name,
        "side": "buy",
        "symbol": symbol,
        "price": price,
        "qty": qty,
        "amount_usdt": usdt_amount,
        "fee": fee,
        "profit": None,
        "balance_after": balance_after,
        "note": str(result)
    }
    
    save_trade(trade_data)
    print("Сделка сохранена в БД")
    
    # Проверяем БД
    conn = sqlite3.connect('bot/trades.db')
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM trades")
    trades = cur.fetchall()
    print(f"Сделок в БД: {len(trades)}")
    for trade in trades:
        print(f"Сделка: {trade}")
    
    cur.execute("SELECT * FROM balances")
    balances = cur.fetchall()
    print(f"Балансов в БД: {len(balances)}")
    for balance in balances:
        print(f"Баланс: {balance}")
    
    conn.close()
    
    print("\n🎉 Детальное тестирование завершено!")


if __name__ == "__main__":
    test_detailed()
