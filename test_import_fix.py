#!/usr/bin/env python3
"""
Тест исправления импорта get_profit_statistics_no_fees
"""

import os
import sys

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_import_fix():
    """Тест импорта функции анализа стратегии"""
    print("🧪 Тест импорта get_profit_statistics_no_fees")
    
    try:
        # Тестируем импорт из db.py
        from bot.db import get_profit_statistics_no_fees, get_profit_statistics
        print("   ✅ Импорт из bot.db успешен")
        
        # Тестируем вызов функции
        stats_no_fees = get_profit_statistics_no_fees()
        stats_with_fees = get_profit_statistics()
        
        print(f"   ✅ Функция get_profit_statistics_no_fees работает")
        print(f"   📊 Результат: {stats_no_fees}")
        
        # Проверяем наличие всех ключей
        required_keys = ['total_profit_no_fees', 'profitable_trades_no_fees', 
                        'losing_trades_no_fees', 'win_rate_no_fees']
        
        for key in required_keys:
            if key not in stats_no_fees:
                print(f"   ❌ Отсутствует ключ: {key}")
                return False
        
        print("   ✅ Все необходимые ключи присутствуют")
        
        # Тест команды /strategy
        print("\n🤖 Тест логики команды /strategy:")
        
        # Эмулируем логику из telegram_bot.py
        profit_emoji_no_fees = "💚" if stats_no_fees['total_profit_no_fees'] > 0 else "❤️" if stats_no_fees['total_profit_no_fees'] < 0 else "💛"
        
        strategy_text = f"""
🧪 Анализ стратегии (БЕЗ комиссий):

{profit_emoji_no_fees} Общая прибыль БЕЗ комиссий: ${stats_no_fees['total_profit_no_fees']:.4f}
📊 Средняя прибыль БЕЗ комиссий: ${stats_no_fees['avg_profit_no_fees']:.4f}
🎯 Процент успеха БЕЗ комиссий: {stats_no_fees['win_rate_no_fees']:.1f}%

Сравнение с учетом комиссий:
• БЕЗ комиссий: ${stats_no_fees['total_profit_no_fees']:.4f}
• С комиссиями: ${stats_with_fees['total_profit']:.4f}
        """
        
        print("   ✅ Формирование сообщения /strategy работает")
        print(f"   📱 Пример вывода:\n{strategy_text.strip()}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка выполнения: {e}")
        return False

if __name__ == "__main__":
    success = test_import_fix()
    if success:
        print("\n🎉 Все тесты пройдены! Команда /strategy будет работать.")
    else:
        print("\n❌ Тесты не пройдены. Требуются дополнительные исправления.")
