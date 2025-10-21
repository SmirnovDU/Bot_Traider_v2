#!/usr/bin/env python3
"""
Railway deployment entry point
Запуск автономного торгового бота на Railway
"""

import asyncio
import os
import sys
import threading
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Импортируем модули
from autonomous_trading_bot import AutonomousTradingBot
from health_server import run_health_server


async def run_bot():
    """Запуск торгового бота"""
    try:
        bot = AutonomousTradingBot()
        await bot.run()
    except Exception as e:
        print(f"Ошибка в торговом боте: {e}")
        raise


async def main():
    """Главная функция для Railway"""
    try:
        # Запускаем health сервер в фоне
        health_task = asyncio.create_task(run_health_server())
        
        # Небольшая задержка для запуска health сервера
        await asyncio.sleep(2)
        
        # Запускаем торговый бот
        bot_task = asyncio.create_task(run_bot())
        
        # Ждем завершения любой из задач
        done, pending = await asyncio.wait(
            [health_task, bot_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Отменяем оставшиеся задачи
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
    except KeyboardInterrupt:
        print("Получен сигнал прерывания")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Запускаем бота и health сервер
    asyncio.run(main())
