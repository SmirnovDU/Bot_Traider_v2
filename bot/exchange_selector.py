from loguru import logger
from bot.exchanges.bybit import BybitExchange
from bot.exchanges.binance import BinanceExchange
from bot.db import get_balance
from bot.config import TEST_MODE


class ExchangeSelector:
    """Выбор биржи на основе лучшей цены и достаточности средств"""

    def __init__(self):
        self.bybit = BybitExchange()
        self.binance = BinanceExchange()

    def get_best_price_exchange(self, symbol, usdt_amount):
        """
        Получает цены с обеих бирж и возвращает биржу с лучшей ценой
        и достаточными средствами
        """
        try:
            # Получаем цены с обеих бирж
            bybit_price = self.bybit.get_last_price(symbol)
            binance_price = self.binance.get_last_price(symbol)
            
            logger.info(f"Цены {symbol}: Bybit={bybit_price}, Binance={binance_price}")
            
            # Получаем балансы USDT
            if TEST_MODE:
                # В тестовом режиме берём балансы из БД
                bybit_balance = get_balance("Bybit", "USDT")
                binance_balance = get_balance("Binance", "USDT")
                logger.info(f"Балансы из БД: Bybit={bybit_balance}, Binance={binance_balance}")
            else:
                # В боевом режиме получаем балансы через API
                bybit_balance = self.bybit.get_balance("USDT")
                binance_balance = self.binance.get_balance("USDT")
                logger.info(f"Балансы из API: Bybit={bybit_balance}, Binance={binance_balance}")
            
            # Рассчитываем стоимость сделки для каждой биржи
            bybit_cost = usdt_amount
            binance_cost = usdt_amount
            
            # Проверяем достаточность средств на обеих биржах
            bybit_sufficient = bybit_balance >= bybit_cost
            binance_sufficient = binance_balance >= binance_cost
            
            logger.info(f"Достаточность средств: Bybit={bybit_sufficient}, Binance={binance_sufficient}")
            
            # Выбираем биржу с лучшей ценой
            if bybit_price <= binance_price:
                # Bybit имеет лучшую цену
                if bybit_sufficient:
                    logger.info(f"Выбрана биржа Bybit (лучшая цена: {bybit_price}, средства: есть)")
                    return self.bybit, bybit_price
                elif binance_sufficient:
                    logger.info(f"Выбрана биржа Binance (Bybit недостаточно средств, Binance: {binance_price})")
                    return self.binance, binance_price
                else:
                    raise ValueError(f"Недостаточно средств на обеих биржах. Нужно: {usdt_amount} USDT")
            else:
                # Binance имеет лучшую цену
                if binance_sufficient:
                    logger.info(f"Выбрана биржа Binance (лучшая цена: {binance_price}, средства: есть)")
                    return self.binance, binance_price
                elif bybit_sufficient:
                    logger.info(f"Выбрана биржа Bybit (Binance недостаточно средств, Bybit: {bybit_price})")
                    return self.bybit, bybit_price
                else:
                    raise ValueError(f"Недостаточно средств на обеих биржах. Нужно: {usdt_amount} USDT")
                
        except Exception as e:
            logger.error(f"Ошибка получения цен: {e}")
            # В случае ошибки используем Bybit как fallback
            fallback_price = self.bybit.get_last_price(symbol)
            
            if TEST_MODE:
                fallback_balance = get_balance("Bybit", "USDT")
            else:
                fallback_balance = self.bybit.get_balance("USDT")
            
            if fallback_balance >= usdt_amount:
                logger.info(f"Используем Bybit как fallback (цена: {fallback_price}, средства: есть)")
                return self.bybit, fallback_price
            else:
                raise ValueError(f"Недостаточно средств на Bybit (fallback). Нужно: {usdt_amount} USDT, есть: {fallback_balance} USDT")

    def get_exchange_by_name(self, exchange_name):
        """Получить биржу по имени"""
        if exchange_name.lower() == "bybit":
            return self.bybit
        elif exchange_name.lower() == "binance":
            return self.binance
        else:
            raise ValueError(f"Неизвестная биржа: {exchange_name}")
