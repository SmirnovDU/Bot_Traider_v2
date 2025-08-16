#!/usr/bin/env python3

import os
import sys
import asyncio

# Устанавливаем переменные окружения
os.environ['TEST_MODE'] = 'True'
os.environ['WEBHOOK_SECRET'] = 'test_secret'
os.environ['DEFAULT_EXCHANGE'] = 'bybit'
os.environ['TEST_BALANCE_USDT'] = '1000'

# Добавляем путь к модулям
sys.path.append('bot')

async def test_telegram_balances():
    """Тестирование команды /balances в Telegram боте"""
    print("Тестирование команды /balances...")
    
    from bot.db import init_db, init_test_balances, get_all_balances
    from bot.telegram_bot import TelegramBot
    from unittest.mock import AsyncMock
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Проверяем что есть балансы
    balances = get_all_balances()
    print(f"Балансы в БД: {balances}")
    
    # Создаём Telegram бота
    bot = TelegramBot()
    
    # Mock отправки сообщений
    sent_messages = []
    
    async def mock_send(message):
        sent_messages.append(message)
        print(f"📱 Отправлено: {message}")
        
    bot.send_message = mock_send
    
    # Тестируем команду /balances
    try:
        await bot.handle_balances()
        
        if sent_messages:
            message = sent_messages[0]
            print(f"\n✅ Команда /balances работает!")
            print(f"Сообщение содержит: {len(message)} символов")
            
            # Проверяем что есть данные о балансах
            if "Bybit" in message or "Binance" in message:
                print("✅ Сообщение содержит данные о биржах")
            else:
                print("❌ Сообщение не содержит данных о биржах")
                
            if "USDT" in message or "DOT" in message:
                print("✅ Сообщение содержит данные о монетах")
            else:
                print("❌ Сообщение не содержит данных о монетах")
                
        else:
            print("❌ Сообщение не отправлено")
            
    except Exception as e:
        print(f"❌ Ошибка в handle_balances: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_balances())
