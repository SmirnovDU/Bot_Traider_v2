#!/usr/bin/env python3
"""
Утилита для проверки статуса Telegram webhook
"""

import asyncio
import aiohttp
from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_WEBHOOK_URL, TELEGRAM_ENABLED


async def check_webhook_info():
    """Проверяет информацию о текущем webhook"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не настроен")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        result = data.get("result", {})
                        
                        print("📡 Информация о Telegram webhook:")
                        print("=" * 40)
                        print(f"URL: {result.get('url', 'Не настроен')}")
                        print(f"Последняя ошибка: {result.get('last_error_message', 'Нет')}")
                        print(f"Время последней ошибки: {result.get('last_error_date', 'Нет')}")
                        print(f"Ожидающих обновлений: {result.get('pending_update_count', 0)}")
                        print(f"Максимальных соединений: {result.get('max_connections', 'Не указано')}")
                        print(f"Разрешённые обновления: {result.get('allowed_updates', 'Все')}")
                        
                        # Проверяем активность
                        webhook_url = result.get('url', '')
                        if webhook_url:
                            print(f"\n✅ Webhook активен: {webhook_url}")
                            
                            # Проверяем, совпадает ли с нашим URL
                            if TELEGRAM_BOT_WEBHOOK_URL and TELEGRAM_BOT_WEBHOOK_URL in webhook_url:
                                print("✅ URL совпадает с настройками")
                            elif TELEGRAM_BOT_WEBHOOK_URL:
                                print(f"⚠️  URL не совпадает с настройками: {TELEGRAM_BOT_WEBHOOK_URL}")
                            
                            # Проверяем ошибки
                            if result.get('last_error_message'):
                                print(f"⚠️  Есть ошибки: {result.get('last_error_message')}")
                            else:
                                print("✅ Ошибок нет")
                        else:
                            print("\n❌ Webhook не настроен")
                            print("💡 Возможные решения:")
                            print("   1. Добавьте TELEGRAM_BOT_WEBHOOK_URL в .env")
                            print("   2. Перезапустите бота для автоматической настройки")
                            
                    else:
                        print(f"❌ Ошибка API: {data}")
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
                    
    except Exception as e:
        print(f"❌ Исключение: {e}")


async def test_webhook_endpoint():
    """Тестирует наш webhook endpoint"""
    if not TELEGRAM_BOT_WEBHOOK_URL:
        print("\n❌ TELEGRAM_BOT_WEBHOOK_URL не настроен, пропускаем тест endpoint")
        return
    
    print(f"\n🧪 Тестирование endpoint: {TELEGRAM_BOT_WEBHOOK_URL}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Тестируем GET запрос
            async with session.get(TELEGRAM_BOT_WEBHOOK_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GET запрос успешен: {data}")
                else:
                    print(f"❌ GET запрос неуспешен: {response.status}")
            
            # Тестируем POST запрос с тестовыми данными
            test_data = {
                "message": {
                    "chat": {"id": "test"},
                    "text": "/help"
                }
            }
            
            async with session.post(TELEGRAM_BOT_WEBHOOK_URL, json=test_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ POST запрос успешен: {data}")
                else:
                    print(f"❌ POST запрос неуспешен: {response.status}")
                    
    except Exception as e:
        print(f"❌ Ошибка тестирования endpoint: {e}")


async def main():
    """Главная функция"""
    print("🔍 Проверка Telegram webhook")
    print("=" * 50)
    
    # Проверяем настройки
    if not TELEGRAM_ENABLED:
        print("❌ Telegram отключен (TELEGRAM_ENABLED=False)")
        return
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не настроен")
        return
    
    print("✅ Telegram настроен")
    print(f"🔧 Webhook URL: {TELEGRAM_BOT_WEBHOOK_URL or 'Не настроен'}")
    
    # Проверяем информацию о webhook
    await check_webhook_info()
    
    # Тестируем endpoint (если настроен)
    await test_webhook_endpoint()
    
    print("\n🏁 Проверка завершена!")


if __name__ == "__main__":
    # Настройка окружения
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Запуск проверки
    asyncio.run(main())
