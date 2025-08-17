#!/usr/bin/env python3
"""
Тест расчета портфеля
"""

import os
import sys

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_portfolio():
    """Тест расчета портфеля"""
    print("🧪 Тест расчета портфеля")
    
    try:
        from bot.portfolio_calculator import portfolio_calculator
        from bot.db import get_all_balances
        from bot.config import USE_MYSQL
        
        print(f"   Режим БД: {'MySQL' if USE_MYSQL else 'SQLite'}")
        
        # Показываем текущие балансы
        balances = get_all_balances()
        print(f"\n💰 Текущие балансы ({len(balances)} записей):")
        
        for balance in balances:
            print(f"   {balance['exchange']} {balance['coin']}: {balance['amount']:.6f}")
        
        # Рассчитываем портфель
        print(f"\n📊 Расчет портфеля:")
        portfolio = portfolio_calculator.get_total_portfolio_usdt()
        
        print(f"   Общий портфель: ${portfolio['total_usdt']:.2f}")
        
        for exchange, data in portfolio['breakdown'].items():
            if data['total'] > 0:
                print(f"   {exchange}:")
                print(f"     USDT: ${data['USDT']:.2f}")
                print(f"     Монеты: ${data['coins_usdt']:.2f}")
                print(f"     Итого: ${data['total']:.2f}")
        
        # Форматируем для Telegram
        portfolio_text = portfolio_calculator.format_portfolio_text(portfolio)
        print(f"\n📱 Telegram формат:")
        print(portfolio_text)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_portfolio()
