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

def test_new_fees():
    print("Тестирование нового расчёта комиссий...")
    
    # Импортируем модули
    from bot.db import init_db, init_test_balances, get_balance, update_balance
    from bot.exchanges.bybit import BybitExchange
    from bot.utils import calculate_fee_for_buy, calculate_fee_for_sell
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Создаём биржу
    bybit = BybitExchange()
    
    print(f"Начальный баланс USDT: {bybit.get_balance('USDT')}")
    
    # Тест 1: Покупка
    print("\n1. Тестируем покупку BTC...")
    symbol = "BTCUSDT"
    usdt_amount = 100
    price = bybit.get_last_price(symbol)
    
    # Получаем баланс перед сделкой
    usdt_before = bybit.get_balance("USDT")
    coin_before = bybit.get_balance(symbol.replace("USDT", ""))
    
    print(f"Баланс USDT до: {usdt_before}")
    print(f"Баланс BTC до: {coin_before}")
    print(f"Покупаем на {usdt_amount} USDT по цене {price}")
    
    # Выполняем покупку
    qty = usdt_amount / price
    result = bybit.place_order("buy", symbol, qty, "quoteCoin")
    
    # Получаем баланс после сделки
    usdt_after = bybit.get_balance("USDT")
    coin_after = bybit.get_balance(symbol.replace("USDT", ""))
    
    print(f"Баланс USDT после: {usdt_after}")
    print(f"Баланс BTC после: {coin_after}")
    print(f"Комиссия из результата: {result['fee']}")
    
    # Проверяем расчёт комиссии
    expected_fee = calculate_fee_for_buy(usdt_before, usdt_after, usdt_amount, price)
    print(f"Ожидаемая комиссия: {expected_fee}")
    
    if abs(result['fee'] - expected_fee) < 0.01:
        print("✅ Комиссия рассчитана правильно")
    else:
        print("❌ Ошибка в расчёте комиссии")
    
    # Тест 2: Продажа
    print("\n2. Тестируем продажу BTC...")
    
    # Получаем баланс перед продажей
    usdt_before_sell = bybit.get_balance("USDT")
    coin_before_sell = bybit.get_balance(symbol.replace("USDT", ""))
    
    print(f"Баланс USDT до продажи: {usdt_before_sell}")
    print(f"Баланс BTC до продажи: {coin_before_sell}")
    
    # Выполняем продажу
    result_sell = bybit.place_order("sell", symbol, coin_before_sell, "baseCoin")
    
    # Получаем баланс после продажи
    usdt_after_sell = bybit.get_balance("USDT")
    coin_after_sell = bybit.get_balance(symbol.replace("USDT", ""))
    
    print(f"Баланс USDT после продажи: {usdt_after_sell}")
    print(f"Баланс BTC после продажи: {coin_after_sell}")
    print(f"Комиссия из результата: {result_sell['fee']}")
    
    # Проверяем расчёт комиссии для продажи
    deal_value = coin_before_sell * price
    expected_fee_sell = calculate_fee_for_sell(usdt_before_sell, usdt_after_sell, deal_value)
    print(f"Ожидаемая комиссия: {expected_fee_sell}")
    
    if abs(result_sell['fee'] - expected_fee_sell) < 0.01:
        print("✅ Комиссия при продаже рассчитана правильно")
    else:
        print("❌ Ошибка в расчёте комиссии при продаже")
    
    print("\n🎉 Тестирование комиссий завершено!")


if __name__ == "__main__":
    test_new_fees()
