#!/usr/bin/env python3
"""
Скрипт для запуска автономного торгового бота
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_trading_bot import AutonomousTradingBot


async def main():
    """Главная функция запуска"""
    print("🤖 Автономный торговый бот v2.0")
    print("=" * 50)
    
    # Проверяем наличие конфигурации
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"❌ Файл конфигурации {config_path} не найден!")
        print("Создайте файл config.yaml на основе примера")
        sys.exit(1)
    
    try:
        # Создаем и запускаем бота
        bot = AutonomousTradingBot(config_path)
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
