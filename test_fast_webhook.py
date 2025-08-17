#!/usr/bin/env python3
"""
Тест быстрой обработки webhook с биржей из сигнала
"""

import os
import sys
import json

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_fast_webhook():
    """Тест новой быстрой логики webhook"""
    print("🚀 Тест быстрой обработки webhook")
    
    try:
        from bot.exchange_selector import ExchangeSelector
        
        # Тестируем упрощенный селектор
        selector = ExchangeSelector()
        
        print("\n🔧 Тест селектора биржи:")
        
        # Тест получения биржи по имени
        bybit = selector.get_exchange_by_name("bybit")
        print(f"   bybit -> {bybit.name}")
        
        binance = selector.get_exchange_by_name("binance")
        print(f"   binance -> {binance.name}")
        
        # Тест неизвестной биржи
        unknown = selector.get_exchange_by_name("unknown")
        print(f"   unknown -> {unknown.name} (должен быть Bybit по умолчанию)")
        
        print("\n📨 Тест новых JSON сигналов:")
        
        # Примеры новых сигналов
        signals = [
            {
                "secret": "kljGCCKJS78ef6vLKGA88",
                "action": "buy",
                "symbol": "BTCUSDT",
                "usdt_amount": "10",
                "exchange": "bybit"
            },
            {
                "secret": "kljGCCKJS78ef6vLKGA88", 
                "action": "sell",
                "symbol": "ETHUSDT",
                "usdt_amount": "10",
                "exchange": "binance"
            }
        ]
        
        for i, signal in enumerate(signals, 1):
            print(f"   Сигнал {i}: {json.dumps(signal, ensure_ascii=False)}")
            
            # Проверяем что биржа корректно извлекается
            exchange_name = signal.get("exchange", "bybit").lower()
            exchange = selector.get_exchange_by_name(exchange_name)
            
            print(f"     -> Биржа: {exchange.name}")
            print(f"     -> Действие: {signal['action']}")
            print(f"     -> Символ: {signal['symbol']}")
        
        print("\n⚡ Преимущества новой логики:")
        print("   ✅ Нет запросов к двум биржам одновременно")
        print("   ✅ Нет сравнения цен")
        print("   ✅ Быстрая обработка сигналов")
        print("   ✅ Биржа указывается в TradingView")
        print("   ✅ Меньше задержек при исполнении")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fast_webhook()
