"""
Универсальный модуль базы данных.
Автоматически выбирает MySQL или SQLite в зависимости от конфигурации.
"""

from loguru import logger
from bot.config import USE_MYSQL

if USE_MYSQL:
    try:
        # Импортируем все функции из MySQL модуля
        from bot.db_mysql import (
            init_db, init_test_balances, get_last_buy_price, has_previous_buy,
            get_unsold_quantity, get_exchange_with_coins, save_trade, get_balance,
            update_balance, get_all_balances, get_profit_statistics, get_trades_summary
        )
        logger.info("🗄️ Используется MySQL база данных")
    except ImportError as e:
        logger.error(f"Ошибка импорта MySQL: {e}. Переключаемся на SQLite")
        # Импортируем SQLite функции как fallback
        from bot.db_sqlite import *
        logger.info("🗄️ Используется SQLite база данных (fallback)")
else:
    # Импортируем SQLite функции
    from bot.db_sqlite import *
    logger.info("🗄️ Используется SQLite база данных")
