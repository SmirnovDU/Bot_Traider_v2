#!/usr/bin/env python3
"""
Быстрый тест основных компонентов бота
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест импортов"""
    print("🔍 Тестирование импортов...")
    
    try:
        from bot.data_fetcher import DataManager
        print("✅ DataManager импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта DataManager: {e}")
        return False
    
    try:
        from bot.indicators import TechnicalIndicators
        print("✅ TechnicalIndicators импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта TechnicalIndicators: {e}")
        return False
    
    try:
        from bot.strategy import TradingStrategy
        print("✅ TradingStrategy импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта TradingStrategy: {e}")
        return False
    
    try:
        from bot.trading_engine import TradingEngine
        print("✅ TradingEngine импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта TradingEngine: {e}")
        return False
    
    try:
        from bot.notifications import NotificationManager
        print("✅ NotificationManager импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта NotificationManager: {e}")
        return False
    
    return True

def test_config():
    """Тест конфигурации"""
    print("\n⚙️ Тестирование конфигурации...")
    
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"❌ Файл конфигурации {config_path} не найден!")
        return False
    
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✅ Конфигурация загружена")
        
        # Проверяем основные секции
        required_sections = ['exchanges', 'trading', 'strategy', 'notifications']
        for section in required_sections:
            if section in config:
                print(f"✅ Секция {section} найдена")
            else:
                print(f"⚠️ Секция {section} отсутствует")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_dependencies():
    """Тест зависимостей"""
    print("\n📦 Тестирование зависимостей...")
    
    dependencies = [
        'ccxt',
        'pandas',
        'numpy',
        'yaml',
        'loguru',
        'aiohttp'
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} не установлен")
            all_ok = False
    
    return all_ok

def main():
    """Главная функция"""
    print("🧪 Быстрый тест автономного торгового бота")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_config,
        test_imports
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ Все тесты пройдены! Бот готов к работе.")
        print("\nДля запуска используйте:")
        print("python autonomous_trading_bot.py")
        print("или")
        print("python run_bot.py")
    else:
        print("❌ Некоторые тесты не пройдены. Проверьте ошибки выше.")
        print("\nВозможные решения:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Проверьте файл config.yaml")
        print("3. Убедитесь, что все модули на месте")

if __name__ == "__main__":
    main()
