"""
Упрощенный селектор биржи - только получение биржи по имени
"""

from loguru import logger
from bot.exchanges.bybit import BybitExchange
from bot.exchanges.binance import BinanceExchange


class ExchangeSelector:
    """Получение биржи по имени (без сравнения цен)"""

    def __init__(self):
        self.bybit = BybitExchange()
        self.binance = BinanceExchange()

    def get_exchange_by_name(self, exchange_name):
        """Получить биржу по имени"""
        exchange_name = exchange_name.lower().strip()
        
        if exchange_name in ["bybit", "bybit_exchange"]:
            logger.debug(f"Выбрана биржа: Bybit")
            return self.bybit
        elif exchange_name in ["binance", "binance_exchange"]:
            logger.debug(f"Выбрана биржа: Binance")
            return self.binance
        else:
            logger.warning(f"Неизвестная биржа '{exchange_name}', используем Bybit по умолчанию")
            return self.bybit
