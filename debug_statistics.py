#!/usr/bin/env python3
"""
Диагностика статистических показателей
"""

import os
import sys

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def debug_statistics():
    """Анализ статистики прибыли"""
    print("🔍 Диагностика статистических показателей")
    
    try:
        from bot.db import get_profit_statistics, get_trades_summary
        from bot.config import USE_MYSQL
        
        print(f"   Режим БД: {'MySQL' if USE_MYSQL else 'SQLite'}")
        
        # Получаем все сделки
        summary = get_trades_summary()
        recent_trades = summary['recent_trades']
        total_trades = summary['total_trades']
        
        print(f"\n📊 Общее количество сделок: {total_trades}")
        
        if recent_trades:
            print("\n🕒 Последние сделки:")
            for i, trade in enumerate(recent_trades):
                print(f"   {i+1}. {trade['timestamp'][:16]} | {trade['exchange']} {trade['side']} {trade['symbol']} | ${trade['amount_usdt']:.2f} | Profit: {trade.get('profit', 'N/A')}")
        
        # Получаем статистику прибыли
        stats = get_profit_statistics()
        
        print(f"\n📈 Статистика прибыли:")
        print(f"   💰 Общая прибыль: ${stats['total_profit']:.4f}")
        print(f"   📊 Средняя прибыль: ${stats['avg_profit']:.4f}")
        print(f"   🎯 Процент успеха: {stats['win_rate']:.1f}%")
        print(f"   ✅ Прибыльных сделок: {stats['profitable_trades']}")
        print(f"   ❌ Убыточных сделок: {stats['losing_trades']}")
        print(f"   📋 Всего сделок с P&L: {stats['total_trades_with_profit']}")
        print(f"   🏆 Лучшая сделка: ${stats['best_trade']:.4f}")
        print(f"   📉 Худшая сделка: ${stats['worst_trade']:.4f}")
        print(f"   💸 Общие комиссии: ${stats['total_fees']:.4f}")
        print(f"   📊 Объём торгов: ${stats['total_volume']:.2f}")
        
        # Проверяем соответствие
        print(f"\n🔍 Проверка соответствия:")
        print(f"   Общее количество сделок: {total_trades}")
        print(f"   Сделок с прибылью: {stats['total_trades_with_profit']}")
        print(f"   Прибыльных + убыточных: {stats['profitable_trades'] + stats['losing_trades']}")
        
        if stats['total_trades_with_profit'] != stats['profitable_trades'] + stats['losing_trades']:
            print("   ⚠️ НЕСООТВЕТСТВИЕ в подсчете сделок!")
        else:
            print("   ✅ Подсчет сделок корректен")
            
        # Анализ отдельных сделок
        print(f"\n🧮 Ручной подсчет:")
        
        if USE_MYSQL:
            import mysql.connector
            from bot.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
            
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
        else:
            import sqlite3
            from bot.config import DB_PATH
            conn = sqlite3.connect(DB_PATH)
            
        cur = conn.cursor()
        
        # Подробный анализ сделок с profit
        cur.execute("SELECT side, profit, amount_usdt FROM trades WHERE profit IS NOT NULL ORDER BY timestamp")
        profit_trades = cur.fetchall()
        
        manual_total_profit = 0
        manual_profitable = 0
        manual_losing = 0
        
        print("   Сделки с прибылью:")
        for side, profit, amount in profit_trades:
            profit_val = float(profit) if profit is not None else 0.0
            manual_total_profit += profit_val
            
            if profit_val > 0:
                manual_profitable += 1
                status = "💚"
            elif profit_val < 0:
                manual_losing += 1
                status = "❤️"
            else:
                status = "💛"
                
            print(f"     {status} {side} ${amount:.2f} -> profit: ${profit_val:.4f}")
        
        print(f"\n   📊 Ручной подсчет:")
        print(f"     Общая прибыль: ${manual_total_profit:.4f}")
        print(f"     Прибыльных: {manual_profitable}")
        print(f"     Убыточных: {manual_losing}")
        
        # Сравнение
        print(f"\n⚖️ Сравнение:")
        print(f"   Общая прибыль: БД ${stats['total_profit']:.4f} vs Ручной ${manual_total_profit:.4f}")
        print(f"   Прибыльных: БД {stats['profitable_trades']} vs Ручной {manual_profitable}")
        print(f"   Убыточных: БД {stats['losing_trades']} vs Ручной {manual_losing}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_statistics()
