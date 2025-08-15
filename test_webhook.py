#!/usr/bin/env python3

import os
import sys
import requests
import json
import time

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '100'

# Добавляем путь к модулям
sys.path.append('bot')

def test_webhook():
    print("Тестирование webhook API...")
    
    # Импортируем FastAPI приложение
    from bot.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Тест 1: Проверка статуса
    print("\n1. Тестируем статус API...")
    response = client.get("/")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    # Тест 2: Проверка балансов
    print("\n2. Тестируем получение балансов...")
    response = client.get("/balances")
    print(f"Статус: {response.status_code}")
    print(f"Балансы: {response.json()}")
    
    # Тест 3: Тестируем покупку
    print("\n3. Тестируем покупку BTC...")
    buy_data = {
        "secret": "test_secret",
        "action": "buy",
        "symbol": "BTCUSDT",
        "usdt_amount": 10
    }
    response = client.post("/webhook", json=buy_data)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    # Тест 4: Тестируем продажу
    print("\n4. Тестируем продажу BTC...")
    sell_data = {
        "secret": "test_secret",
        "action": "sell",
        "symbol": "BTCUSDT"
    }
    response = client.post("/webhook", json=sell_data)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    # Тест 5: Проверяем балансы после сделок
    print("\n5. Проверяем балансы после сделок...")
    response = client.get("/balances")
    print(f"Статус: {response.status_code}")
    print(f"Балансы: {response.json()}")
    
    print("\n🎉 Тестирование webhook завершено!")


if __name__ == "__main__":
    test_webhook()
