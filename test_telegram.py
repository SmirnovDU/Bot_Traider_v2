#!/usr/bin/env python3
"""
Тест для проверки работы Telegram уведомлений
"""

import asyncio
import os
from bot.telegram_notifier import notify_trade, notify_error, notify_status

# Пример данных сделки
SAMPLE_TRADE_DATA = {
    "request_id": "BUY_BTCUSDT_1234567890",
    "timestamp": "2024-01-15T10:30:00Z",
    "exchange": "Bybit",
    "side": "buy",
    "symbol": "BTCUSDT",
    "price": 45000.50,
    "qty": 0.001,
    "amount_usdt": 45.0,
    "fee": 0.045,
    "profit": None,
    "balance_after": 955.0,
    "note": "Test order"
}

SAMPLE_SELL_TRADE_DATA = {
    "request_id": "SELL_BTCUSDT_1234567891",
    "timestamp": "2024-01-15T11:30:00Z",
    "exchange": "Binance",
    "side": "sell",
    "symbol": "BTCUSDT",
    "price": 45200.75,
    "qty": 0.001,
    "amount_usdt": 45.2,
    "fee": 0.0452,
    "profit": 0.1548,  # Положительная прибыль
    "balance_after": 1000.15,
    "note": "Test sell order"
}


async def test_telegram_notifications():
    """Тестирует все типы Telegram уведомлений"""
    
    print("🧪 Тестирование Telegram уведомлений...")
    print()
    
    # Проверяем настройки
    from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram уведомления отключены в конфигурации")
        print("Установите TELEGRAM_ENABLED=True в .env файле")
        return False
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Не указан TELEGRAM_BOT_TOKEN")
        return False
    
    if not TELEGRAM_CHAT_ID:
        print("❌ Не указан TELEGRAM_CHAT_ID")
        return False
    
    print(f"✅ Telegram настроен для чата: {TELEGRAM_CHAT_ID}")
    print()
    
    # Тест 1: Уведомление о статусе
    print("1️⃣ Тестируем уведомление о статусе...")
    try:
        success = await notify_status("Тест системы уведомлений", {
            "Версия": "4.0",
            "Тест": "Telegram интеграция"
        })
        if success:
            print("✅ Статусное уведомление отправлено")
        else:
            print("❌ Ошибка отправки статусного уведомления")
    except Exception as e:
        print(f"❌ Исключение при отправке статусного уведомления: {e}")
    
    await asyncio.sleep(2)  # Пауза между сообщениями
    
    # Тест 2: Уведомление о покупке
    print("\n2️⃣ Тестируем уведомление о покупке...")
    try:
        success = await notify_trade(SAMPLE_TRADE_DATA)
        if success:
            print("✅ Уведомление о покупке отправлено")
        else:
            print("❌ Ошибка отправки уведомления о покупке")
    except Exception as e:
        print(f"❌ Исключение при отправке уведомления о покупке: {e}")
    
    await asyncio.sleep(2)
    
    # Тест 3: Уведомление о продаже с прибылью
    print("\n3️⃣ Тестируем уведомление о продаже...")
    try:
        success = await notify_trade(SAMPLE_SELL_TRADE_DATA)
        if success:
            print("✅ Уведомление о продаже отправлено")
        else:
            print("❌ Ошибка отправки уведомления о продаже")
    except Exception as e:
        print(f"❌ Исключение при отправке уведомления о продаже: {e}")
    
    await asyncio.sleep(2)
    
    # Тест 4: Уведомление об ошибке
    print("\n4️⃣ Тестируем уведомление об ошибке...")
    try:
        success = await notify_error("Тестовая ошибка для проверки уведомлений", "Тест системы")
        if success:
            print("✅ Уведомление об ошибке отправлено")
        else:
            print("❌ Ошибка отправки уведомления об ошибке")
    except Exception as e:
        print(f"❌ Исключение при отправке уведомления об ошибке: {e}")
    
    print("\n🎉 Тестирование завершено!")
    return True


async def test_bot_token():
    """Проверяет валидность токена бота"""
    from bot.config import TELEGRAM_BOT_TOKEN
    import aiohttp
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Токен бота не настроен")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        bot_info = data.get("result", {})
                        print(f"✅ Токен бота валиден: @{bot_info.get('username', 'unknown')}")
                        return True
                    else:
                        print(f"❌ Токен бота невалиден: {data}")
                        return False
                else:
                    print(f"❌ Ошибка API: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        return False


async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов Telegram интеграции")
    print("=" * 50)
    
    # Проверяем токен бота
    print("\n🔑 Проверка токена бота...")
    if not await test_bot_token():
        print("\n❌ Тестирование прервано из-за проблем с токеном")
        return
    
    # Тестируем уведомления
    print("\n📱 Тестирование уведомлений...")
    await test_telegram_notifications()


if __name__ == "__main__":
    # Загружаем переменные окружения для тестов
    from decouple import config
    import sys
    import os
    
    # Добавляем корневую директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Запускаем тесты
    asyncio.run(main())
