#!/usr/bin/env python3
"""
Тест для проверки Telegram команд бота
"""

import asyncio
import json
from bot.telegram_bot import process_telegram_update, telegram_bot
from bot.db import init_db, init_test_balances, save_trade
from datetime import datetime, timezone


# Примеры обновлений от Telegram
SAMPLE_UPDATES = {
    "help": {
        "message": {
            "message_id": 1,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": "123456789", "type": "private"},
            "date": 1673123456,
            "text": "/help"
        }
    },
    "status": {
        "message": {
            "message_id": 2,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": "123456789", "type": "private"},
            "date": 1673123456,
            "text": "/status"
        }
    },
    "balances": {
        "message": {
            "message_id": 3,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": "123456789", "type": "private"},
            "date": 1673123456,
            "text": "/balances"
        }
    },
    "profit": {
        "message": {
            "message_id": 4,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": "123456789", "type": "private"},
            "date": 1673123456,
            "text": "/profit"
        }
    },
    "summary": {
        "message": {
            "message_id": 5,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": "123456789", "type": "private"},
            "date": 1673123456,
            "text": "/summary"
        }
    },
    "unknown": {
        "message": {
            "message_id": 6,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": "123456789", "type": "private"},
            "date": 1673123456,
            "text": "/unknown_command"
        }
    }
}


def setup_test_data():
    """Настройка тестовых данных"""
    print("📊 Настройка тестовых данных...")
    
    # Инициализируем базу данных
    init_db()
    init_test_balances()
    
    # Добавляем тестовые сделки
    test_trades = [
        {
            "request_id": "BUY_BTCUSDT_001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": "Bybit",
            "side": "buy",
            "symbol": "BTCUSDT",
            "price": 45000.0,
            "qty": 0.001,
            "amount_usdt": 45.0,
            "fee": 0.045,
            "profit": None,
            "balance_after": 955.0,
            "note": "Test buy order"
        },
        {
            "request_id": "SELL_BTCUSDT_001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": "Bybit",
            "side": "sell",
            "symbol": "BTCUSDT",
            "price": 45500.0,
            "qty": 0.001,
            "amount_usdt": 45.5,
            "fee": 0.0455,
            "profit": 0.4545,  # Прибыль
            "balance_after": 1000.45,
            "note": "Test sell order"
        },
        {
            "request_id": "BUY_ETHUSDT_001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": "Binance",
            "side": "buy",
            "symbol": "ETHUSDT",
            "price": 3000.0,
            "qty": 0.01,
            "amount_usdt": 30.0,
            "fee": 0.03,
            "profit": None,
            "balance_after": 970.0,
            "note": "Test ETH buy"
        },
        {
            "request_id": "SELL_ETHUSDT_001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": "Binance",
            "side": "sell",
            "symbol": "ETHUSDT",
            "price": 2950.0,
            "qty": 0.01,
            "amount_usdt": 29.5,
            "fee": 0.0295,
            "profit": -0.5595,  # Убыток
            "balance_after": 999.47,
            "note": "Test ETH sell"
        }
    ]
    
    # Сохраняем тестовые сделки
    for trade in test_trades:
        try:
            save_trade(trade)
        except Exception as e:
            print(f"Ошибка сохранения сделки {trade['request_id']}: {e}")
    
    print("✅ Тестовые данные настроены")


async def test_command(command_name: str, update: dict):
    """Тестирует одну команду"""
    print(f"\n🧪 Тестируем команду: {command_name}")
    
    # Заменяем chat_id на корректный из конфигурации
    from bot.config import TELEGRAM_CHAT_ID
    if TELEGRAM_CHAT_ID:
        update["message"]["chat"]["id"] = TELEGRAM_CHAT_ID
    
    try:
        success = await process_telegram_update(update)
        if success:
            print(f"✅ Команда {command_name} выполнена успешно")
        else:
            print(f"❌ Команда {command_name} завершилась с ошибкой")
        return success
    except Exception as e:
        print(f"❌ Исключение при выполнении команды {command_name}: {e}")
        return False


async def test_all_commands():
    """Тестирует все команды"""
    print("🚀 Запуск тестов Telegram команд")
    print("=" * 50)
    
    # Проверяем настройки
    from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram отключен в конфигурации")
        print("Установите TELEGRAM_ENABLED=True в .env файле")
        return False
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Не указан TELEGRAM_BOT_TOKEN")
        return False
    
    if not TELEGRAM_CHAT_ID:
        print("❌ Не указан TELEGRAM_CHAT_ID")
        return False
    
    print(f"✅ Telegram настроен для чата: {TELEGRAM_CHAT_ID}")
    
    # Настраиваем тестовые данные
    setup_test_data()
    
    # Тестируем каждую команду
    results = {}
    
    for command_name, update in SAMPLE_UPDATES.items():
        await asyncio.sleep(1)  # Пауза между командами
        success = await test_command(command_name, update)
        results[command_name] = success
    
    # Результаты
    print("\n📊 Результаты тестирования:")
    print("=" * 30)
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for command, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{command:12} - {status}")
    
    print(f"\nВсего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 Все тесты прошли успешно!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} тестов провалено")
    
    return passed_tests == total_tests


async def test_api_endpoints():
    """Тестирует API endpoints (для сравнения)"""
    print("\n🔗 Тестирование API endpoints...")
    
    import httpx
    
    base_url = "http://localhost:8000"
    get_endpoints = ["/status", "/balances", "/profit", "/telegram-webhook"]
    
    async with httpx.AsyncClient() as client:
        # Тестируем GET endpoints
        for endpoint in get_endpoints:
            try:
                response = await client.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    print(f"✅ GET {endpoint} - OK")
                    data = response.json()
                    print(f"   Данные: {json.dumps(data, indent=2, ensure_ascii=False)[:100]}...")
                else:
                    print(f"❌ GET {endpoint} - Error {response.status_code}")
            except Exception as e:
                print(f"❌ GET {endpoint} - Exception: {e}")
        
        # Тестируем POST telegram-webhook
        print("\n🧪 Тестирование POST /telegram-webhook...")
        test_update = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "/status"
            }
        }
        
        try:
            response = await client.post(f"{base_url}/telegram-webhook", json=test_update)
            if response.status_code == 200:
                print("✅ POST /telegram-webhook - OK")
                data = response.json()
                print(f"   Ответ: {data}")
            else:
                print(f"❌ POST /telegram-webhook - Error {response.status_code}")
        except Exception as e:
            print(f"❌ POST /telegram-webhook - Exception: {e}")


async def main():
    """Главная функция"""
    print("🤖 Тест системы Telegram команд")
    print("=" * 50)
    
    # Тестируем команды
    success = await test_all_commands()
    
    # Тестируем API (опционально)
    print("\n" + "=" * 50)
    await test_api_endpoints()
    
    print("\n🏁 Тестирование завершено!")
    return success


if __name__ == "__main__":
    # Настройка окружения
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Запуск тестов
    asyncio.run(main())
