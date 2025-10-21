#!/usr/bin/env python3
"""
Автономный торговый бот для Binance и Bybit
Версия 2.0 - без TradingView, с собственными индикаторами

Автор: Trading Bot v2.0
Дата: 2024
"""

import asyncio
import yaml
import signal
import sys
import os
from datetime import datetime
from loguru import logger
from typing import Dict, Any

# Импорты модулей бота
from bot.data_fetcher import DataManager
from bot.indicators import TechnicalIndicators
from bot.strategy import TradingStrategy, SignalType
from bot.trading_engine import TradingEngine
from bot.notifications import NotificationManager


class AutonomousTradingBot:
    """Основной класс автономного торгового бота"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Инициализация бота
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False
        self.last_update = None
        
        # Инициализация компонентов
        self.data_manager = None
        self.indicators = None
        self.strategy = None
        self.trading_engine = None
        self.notifications = None
        
        # Настройка логирования
        self._setup_logging()
        
        # Настройка обработчиков сигналов
        self._setup_signal_handlers()
        
        logger.info("Автономный торговый бот инициализирован")
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из YAML файла с поддержкой переменных окружения"""
        try:
            # Загружаем .env файл если он существует
            env_file = os.path.join(os.path.dirname(self.config_path), '.env')
            if os.path.exists(env_file):
                self._load_env_file(env_file)
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_text = f.read()
            
            # Заменяем переменные окружения
            config_text = self._substitute_env_vars(config_text)
            
            config = yaml.safe_load(config_text)
            logger.info(f"Конфигурация загружена из {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Файл конфигурации {self.config_path} не найден")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Ошибка парсинга YAML: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            sys.exit(1)
    
    def _load_env_file(self, env_file: str):
        """Загрузка переменных из .env файла"""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            logger.info(f"Переменные окружения загружены из {env_file}")
        except Exception as e:
            logger.warning(f"Не удалось загрузить .env файл: {e}")
    
    def _substitute_env_vars(self, text: str) -> str:
        """Замена переменных окружения в тексте"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ""
            return os.environ.get(var_name, default_value)
        
        # Паттерн для ${VAR_NAME:default_value} или ${VAR_NAME}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        return re.sub(pattern, replace_var, text)
    
    def _setup_logging(self):
        """Настройка логирования"""
        try:
            logging_config = self.config.get('logging', {})
            level = logging_config.get('level', 'INFO')
            log_file = logging_config.get('file', 'bot.log')
            max_size = logging_config.get('max_size', '10 MB')
            retention = logging_config.get('retention', '7 days')
            compression = logging_config.get('compression', 'zip')
            
            # Удаляем стандартный обработчик
            logger.remove()
            
            # Добавляем консольный вывод
            logger.add(
                sys.stdout,
                level=level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            )
            
            # Добавляем файловый вывод
            logger.add(
                log_file,
                level=level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation=max_size,
                retention=retention,
                compression=compression
            )
            
            logger.info(f"Логирование настроено: уровень {level}, файл {log_file}")
            
        except Exception as e:
            logger.error(f"Ошибка настройки логирования: {e}")
    
    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов для корректного завершения"""
        def signal_handler(signum, frame):
            logger.info(f"Получен сигнал {signum}, завершение работы...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Инициализация всех компонентов бота"""
        try:
            logger.info("Инициализация компонентов бота...")
            
            # Инициализация менеджера данных
            self.data_manager = DataManager(self.config)
            logger.info("Менеджер данных инициализирован")
            
            # Инициализация калькулятора индикаторов
            self.indicators = TechnicalIndicators(self.config)
            logger.info("Калькулятор индикаторов инициализирован")
            
            # Инициализация стратегии
            self.strategy = TradingStrategy(self.config, self.indicators)
            logger.info("Стратегия инициализирована")
            
            # Инициализация торгового движка
            self.trading_engine = TradingEngine(self.config, self.data_manager.fetchers[self.data_manager.default_exchange])
            logger.info("Торговый движок инициализирован")
            
            # Инициализация уведомлений
            self.notifications = NotificationManager(self.config)
            logger.info("Менеджер уведомлений инициализирован")
            
            # Тестирование Telegram подключения
            if self.notifications.telegram_enabled:
                if self.notifications.test_telegram_connection():
                    await self.notifications.send_test_message()
                else:
                    logger.warning("Не удалось подключиться к Telegram")
            
            logger.info("Все компоненты успешно инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise
    
    async def run(self):
        """Основной цикл работы бота"""
        try:
            await self.initialize()
            
            self.running = True
            logger.info("Бот запущен и готов к работе")
            
            # Отправляем уведомление о запуске
            await self.notifications.send_status_notification({
                "Статус": "Запущен",
                "Режим": "Симуляция" if self.trading_engine.simulation_mode else "Реальная торговля",
                "Символ": self.strategy.symbol,
                "Таймфрейм": self.strategy.timeframe
            })
            
            # Получаем настройки обновления
            update_interval = self.config.get('trading', {}).get('update_interval', 900)  # 15 минут по умолчанию
            
            while self.running:
                try:
                    await self._trading_cycle()
                    await asyncio.sleep(update_interval)
                    
                except KeyboardInterrupt:
                    logger.info("Получен сигнал прерывания")
                    break
                except Exception as e:
                    logger.error(f"Ошибка в торговом цикле: {e}")
                    await self.notifications.send_error_notification(str(e), "Торговый цикл")
                    await asyncio.sleep(60)  # Пауза перед повтором
            
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            await self.notifications.send_error_notification(str(e), "Критическая ошибка")
        finally:
            await self.shutdown()
    
    async def _trading_cycle(self):
        """Один цикл торговли"""
        try:
            logger.info("Начало торгового цикла")
            
            # Получаем данные
            symbol = self.strategy.symbol
            timeframe = self.strategy.timeframe
            limit = 100  # Количество свечей для анализа
            
            logger.info(f"Получение данных: {symbol} {timeframe}")
            df = self.data_manager.get_data(symbol, timeframe, limit)
            
            if df.empty:
                logger.warning("Получены пустые данные")
                return
            
            # Рассчитываем индикаторы
            logger.info("Расчет индикаторов")
            df_with_indicators = self.indicators.calculate_all_indicators(df)
            
            # Анализируем рынок
            logger.info("Анализ рынка")
            signal = self.strategy.analyze_market(df_with_indicators)
            
            # Отправляем уведомление о сигнале
            if signal.signal_type != SignalType.HOLD:
                await self.notifications.send_signal_notification(signal)
            
            # Исполняем сигнал
            if signal.signal_type != SignalType.HOLD:
                logger.info(f"Исполнение сигнала: {signal.signal_type.value}")
                success = self.trading_engine.execute_signal(signal)
                
                if success:
                    # Получаем последнюю сделку
                    trades = self.trading_engine.get_trades(limit=1)
                    if trades:
                        await self.notifications.send_trade_notification(trades[-1])
                else:
                    logger.error("Не удалось исполнить сигнал")
            
            # Обновляем позиции
            self.trading_engine.update_positions()
            
            # Обновляем время последнего обновления
            self.last_update = datetime.now()
            
            # Логируем статистику
            self._log_statistics()
            
            logger.info("Торговый цикл завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в торговом цикле: {e}")
            raise
    
    def _log_statistics(self):
        """Логирование статистики"""
        try:
            # Статистика стратегии
            strategy_stats = self.strategy.get_strategy_stats()
            logger.info(f"Стратегия: {strategy_stats['total_signals']} сигналов, "
                       f"позиция: {strategy_stats['current_position'] or 'нет'}")
            
            # Статистика торговли
            trading_stats = self.trading_engine.get_trading_stats()
            logger.info(f"Торговля: {trading_stats['total_trades']} сделок, "
                       f"PnL: {trading_stats['total_pnl']:.4f} USDT")
            
            # Баланс
            balance = self.trading_engine.get_balance()
            usdt_balance = balance.get('USDT', 0)
            logger.info(f"Баланс USDT: {usdt_balance:.4f}")
            
        except Exception as e:
            logger.error(f"Ошибка логирования статистики: {e}")
    
    async def send_daily_report(self):
        """Отправка ежедневного отчета"""
        try:
            stats = {
                'trading_stats': self.trading_engine.get_trading_stats(),
                'strategy_stats': self.strategy.get_strategy_stats(),
                'balance': self.trading_engine.get_balance()
            }
            
            await self.notifications.send_daily_report(stats)
            
        except Exception as e:
            logger.error(f"Ошибка отправки ежедневного отчета: {e}")
    
    def stop(self):
        """Остановка бота"""
        logger.info("Остановка бота...")
        self.running = False
    
    async def shutdown(self):
        """Корректное завершение работы бота"""
        try:
            logger.info("Завершение работы бота...")
            
            # Отправляем уведомление о завершении
            if self.notifications:
                await self.notifications.send_status_notification({
                    "Статус": "Остановлен",
                    "Время работы": f"{self.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_update else 'Неизвестно'}"
                })
            
            # Сохраняем историю сделок
            if self.trading_engine:
                self.trading_engine._save_trade_history()
            
            logger.info("Бот завершил работу")
            
        except Exception as e:
            logger.error(f"Ошибка при завершении работы: {e}")


async def main():
    """Главная функция"""
    try:
        # Создаем и запускаем бота
        bot = AutonomousTradingBot()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
