#!/usr/bin/env python3
"""
Скрипт для тестирования компонентов бота
"""

import asyncio
import sys
import os
import yaml
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from bot.data_fetcher import DataManager
from bot.indicators import TechnicalIndicators
from bot.strategy import TradingStrategy
from bot.trading_engine import TradingEngine
from bot.notifications import NotificationManager


async def test_data_fetcher(config):
    """Тестирование получения данных"""
    print("📊 Тестирование получения данных...")
    
    try:
        data_manager = DataManager(config)
        
        # Тестируем получение данных
        symbol = config.get('trading', {}).get('symbol', 'BTC/USDT')
        timeframe = config.get('trading', {}).get('timeframe', '15m')
        
        print(f"Получение данных {symbol} {timeframe}...")
        df = data_manager.get_data(symbol, timeframe, limit=50)
        
        if not df.empty:
            print(f"✅ Получено {len(df)} свечей")
            print(f"Последняя цена: {df['close'].iloc[-1]:.4f}")
            print(f"Временной диапазон: {df.index[0]} - {df.index[-1]}")
        else:
            print("❌ Не удалось получить данные")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования данных: {e}")


def test_indicators(config):
    """Тестирование расчета индикаторов"""
    print("\n📈 Тестирование индикаторов...")
    
    try:
        indicators = TechnicalIndicators(config)
        
        # Создаем тестовые данные
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=100, freq='15min')
        np.random.seed(42)
        
        # Генерируем тестовые OHLCV данные
        base_price = 50000
        prices = []
        for i in range(100):
            change = np.random.normal(0, 0.02)  # 2% волатильность
            base_price *= (1 + change)
            prices.append(base_price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': [np.random.uniform(100, 1000) for _ in range(100)]
        }, index=dates)
        
        # Рассчитываем индикаторы
        df_with_indicators = indicators.calculate_all_indicators(df)
        
        # Проверяем результаты
        enabled_indicators = indicators.get_enabled_indicators()
        print(f"✅ Включенные индикаторы: {enabled_indicators}")
        
        # Проверяем EMA
        ema_config = indicators.indicators_config['ema']
        fast_col = f"EMA_{ema_config.params['fast']}"
        slow_col = f"EMA_{ema_config.params['slow']}"
        
        if fast_col in df_with_indicators.columns and slow_col in df_with_indicators.columns:
            print(f"✅ EMA рассчитан: {fast_col}, {slow_col}")
            print(f"Последние значения: {fast_col}={df_with_indicators[fast_col].iloc[-1]:.4f}, "
                  f"{slow_col}={df_with_indicators[slow_col].iloc[-1]:.4f}")
        
        # Тестируем сигнал пересечения
        signal = indicators.get_ema_cross_signal(df_with_indicators)
        print(f"✅ Сигнал пересечения EMA: {signal}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования индикаторов: {e}")


async def test_strategy(config):
    """Тестирование стратегии"""
    print("\n🎯 Тестирование стратегии...")
    
    try:
        indicators = TechnicalIndicators(config)
        strategy = TradingStrategy(config, indicators)
        
        # Создаем тестовые данные с индикаторами
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=100, freq='15min')
        np.random.seed(42)
        
        base_price = 50000
        prices = []
        for i in range(100):
            change = np.random.normal(0, 0.02)
            base_price *= (1 + change)
            prices.append(base_price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': [np.random.uniform(100, 1000) for _ in range(100)]
        }, index=dates)
        
        # Рассчитываем индикаторы
        df_with_indicators = indicators.calculate_all_indicators(df)
        
        # Анализируем рынок
        signal = strategy.analyze_market(df_with_indicators)
        
        print(f"✅ Сигнал стратегии: {signal.signal_type.value}")
        print(f"Цена: {signal.price:.4f}")
        print(f"Уверенность: {signal.confidence:.2%}")
        print(f"Причина: {signal.reason}")
        
        # Получаем статистику
        stats = strategy.get_strategy_stats()
        print(f"✅ Статистика стратегии: {stats}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования стратегии: {e}")


async def test_notifications(config):
    """Тестирование уведомлений"""
    print("\n📱 Тестирование уведомлений...")
    
    try:
        notifications = NotificationManager(config)
        
        if not notifications.telegram_enabled:
            print("⚠️ Telegram уведомления отключены в конфигурации")
            return
        
        # Тестируем подключение
        if notifications.test_telegram_connection():
            print("✅ Подключение к Telegram успешно")
            
            # Отправляем тестовое сообщение
            success = await notifications.send_test_message()
            if success:
                print("✅ Тестовое сообщение отправлено")
            else:
                print("❌ Не удалось отправить тестовое сообщение")
        else:
            print("❌ Не удалось подключиться к Telegram")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования уведомлений: {e}")


async def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование компонентов бота")
    print("=" * 50)
    
    # Загружаем конфигурацию
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"❌ Файл конфигурации {config_path} не найден!")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        sys.exit(1)
    
    # Запускаем тесты
    await test_data_fetcher(config)
    test_indicators(config)
    await test_strategy(config)
    await test_notifications(config)
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())