from pybit.unified_trading import HTTP
from loguru import logger
from bot.config import API_KEY_BYBIT, API_SECRET_BYBIT, TEST_MODE, BYBIT_FEE
from bot.db import get_balance, update_balance, get_last_buy_price
from bot.utils import calculate_qty_by_precision, calculate_fee_for_buy, calculate_fee_for_sell
from decimal import Decimal, ROUND_DOWN
from datetime import datetime


class BybitExchange:
    def __init__(self):
        self.name = "Bybit"
        self.fee_percent = BYBIT_FEE
        if not TEST_MODE:
            self.session = HTTP(testnet=False, api_key=API_KEY_BYBIT, api_secret=API_SECRET_BYBIT)
        else:
            self.session = None  # тестовый режим без подключения

    def get_last_price(self, symbol):
        if TEST_MODE:
            # В тестовом режиме используем реальные цены с резервной биржи
            try:
                import requests
                response = requests.get(f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}")
                data = response.json()
                if data["retCode"] == 0 and data["result"]["list"]:
                    price = float(data["result"]["list"][0]["lastPrice"])
                    logger.info(f"Получена реальная цена {symbol} от Bybit: {price}")
                    return price
            except Exception as e:
                logger.warning(f"Не удалось получить реальную цену Bybit в тестовом режиме: {e}")
            return 100.0  # резервная цена
        try:
            ticker = self.session.get_tickers(category="spot", symbol=symbol)
            return float(ticker["result"]["list"][0]["lastPrice"])
        except Exception as e:
            logger.error(f"Ошибка получения цены Bybit: {e}")
            return 100.0

    def get_balance(self, coin):
        if TEST_MODE:
            return get_balance(self.name, coin)
        try:
            balance_data = self.session.get_wallet_balance(accountType="SPOT", coin=coin)
            coins_list = balance_data.get("result", {}).get("list", [])
            if not coins_list:
                return 0.0
            return float(coins_list[0].get("availableToWithdraw", 0))
        except Exception as e:
            logger.error(f"Ошибка получения баланса Bybit: {e}")
            return 0.0

    def place_order(self, side, symbol, qty, market_unit):
        if TEST_MODE:
            # в тестовом режиме сразу обновляем баланс в БД
            price = self.get_last_price(symbol)

            if side.lower() == "buy":
                usdt_balance_before = get_balance(self.name, "USDT")
                coin_balance_before = get_balance(self.name, symbol.replace("USDT", ""))
                
                # Рассчитываем стоимость сделки
                deal_value = qty * price
                
                # Проверяем достаточность средств
                if deal_value > usdt_balance_before:
                    raise ValueError(f"Недостаточно USDT: {usdt_balance_before} < {deal_value}")
                
                # Обновляем балансы
                update_balance(self.name, "USDT", usdt_balance_before - deal_value)
                update_balance(self.name, symbol.replace("USDT", ""), coin_balance_before + qty)
                
                # Получаем баланс после сделки для расчёта комиссии
                usdt_balance_after = get_balance(self.name, "USDT")
                coin_balance_after = get_balance(self.name, symbol.replace("USDT", ""))
                fee = calculate_fee_for_buy(usdt_balance_before, usdt_balance_after, coin_balance_before, coin_balance_after, deal_value, price)
                
            else:
                coin_balance_before = get_balance(self.name, symbol.replace("USDT", ""))
                usdt_balance_before = get_balance(self.name, "USDT")
                
                if qty > coin_balance_before:
                    raise ValueError(f"Недостаточно {symbol.replace('USDT', '')}: {coin_balance_before} < {qty}")
                
                # Рассчитываем стоимость сделки
                deal_value = qty * price
                
                # Обновляем балансы
                update_balance(self.name, symbol.replace("USDT", ""), coin_balance_before - qty)
                update_balance(self.name, "USDT", usdt_balance_before + deal_value)
                
                # Получаем баланс после сделки для расчёта комиссии
                usdt_balance_after = get_balance(self.name, "USDT")
                fee = calculate_fee_for_sell(usdt_balance_before, usdt_balance_after, deal_value)
            
            logger.info(f"[TEST] Ордер {side} {qty} {symbol} по цене {price}, комиссия: {fee}")
            return {
                "status": "test order", 
                "side": side, 
                "symbol": symbol, 
                "qty": qty,
                "price": price,
                "fee": fee
            }
        else:
            try:
                result = self.session.place_order(
                    category="spot",
                    symbol=symbol,
                    side=side.capitalize(),
                    order_type="Market",
                    qty=qty,
                    marketUnit=market_unit
                )
                return result
            except Exception as e:
                logger.error(f"Ошибка размещения ордера Bybit: {e}")
                raise

    def init_balances(self):
        """Инициализация балансов при старте"""
        if not TEST_MODE:
            try:
                # Получаем баланс USDT
                usdt_balance = self.get_balance("USDT")
                update_balance(self.name, "USDT", usdt_balance)
                logger.info(f"Bybit USDT баланс: {usdt_balance}")
            except Exception as e:
                logger.error(f"Ошибка инициализации баланса Bybit: {e}")
