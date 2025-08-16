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

async def test_profit_logic():
    """Тестирование логики прибыли - покупки не должны показывать убытки"""
    print("Тестирование логики прибыли...")
    
    from bot.db import init_db, init_test_balances, get_trades_summary, get_profit_statistics
    from bot.telegram_bot import TelegramBot
    from unittest.mock import AsyncMock
    
    # Инициализируем БД
    init_db()
    init_test_balances()
    
    # Получаем статистику
    trades_summary = get_trades_summary()
    profit_stats = get_profit_statistics()
    
    print(f"📊 Всего сделок: {trades_summary['total_trades']}")
    print(f"💰 Последние сделки: {len(trades_summary['recent_trades'])}")
    print(f"📈 Сделки с прибылью: {profit_stats['total_trades_with_profit']}")
    print(f"💚 Прибыльные: {profit_stats['profitable_trades']}")
    print(f"❤️ Убыточные: {profit_stats['losing_trades']}")
    
    # Анализируем последние сделки
    print("\n🔍 Анализ последних сделок:")
    for i, trade in enumerate(trades_summary['recent_trades'][:5]):
        side = trade['side']
        symbol = trade['symbol']
        profit = trade['profit']
        amount = trade['amount_usdt']
        
        print(f"  {i+1}. {side.upper()} {symbol}: ${amount:.2f} - profit: {profit}")
        
        if side == "buy" and profit is not None and profit != 0:
            print(f"    ⚠️ ПРОБЛЕМА: Покупка не должна иметь прибыль: {profit}")
        elif side == "sell" and profit is None:
            print(f"    ⚠️ ПРОБЛЕМА: Продажа должна иметь прибыль")
        else:
            print(f"    ✅ Корректно")
    
    # Тестируем команду /summary
    print("\n📱 Тестируем команду /summary:")
    
    bot = TelegramBot()
    sent_messages = []
    
    async def mock_send(message):
        sent_messages.append(message)
        print("📤 Отправлено:")
        print(message)
        
    bot.send_message = mock_send
    
    try:
        await bot.handle_summary()
        
        if sent_messages:
            message = sent_messages[0]
            
            # Проверяем что покупки НЕ показывают прибыль
            lines = message.split('\n')
            for line in lines:
                if "🟢" in line and ("❤️$" in line or "💚$" in line):
                    print(f"❌ ОШИБКА: Покупка показывает прибыль: {line}")
                elif "🟢" in line:
                    print(f"✅ Покупка БЕЗ прибыли: {line}")
                elif "🔴" in line and ("❤️$" in line or "💚$" in line):
                    print(f"✅ Продажа С прибылью: {line}")
        else:
            print("❌ Сообщение не отправлено")
            
    except Exception as e:
        print(f"❌ Ошибка в handle_summary: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_profit_logic())
