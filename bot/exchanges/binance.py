from binance.client import Client
from loguru import logger
from bot.config import API_KEY_BINANCE, API_SECRET_BINANCE, TEST_MODE, BINANCE_FEE
from bot.db import get_balance, update_balance, get_last_buy_price
from bot.utils import calculate_qty_by_precision, calculate_fee_for_buy, calculate_fee_for_sell
from datetime import datetime


class BinanceExchange:
    def __init__(self):
        self.name = "Binance"
        self.fee_percent = BINANCE_FEE
        if not TEST_MODE:
            self.client = Client(API_KEY_BINANCE, API_SECRET_BINANCE)
        else:
            self.client = None

    def get_last_price(self, symbol):
        if TEST_MODE:
            # В тестовом режиме используем реальные цены с публичного API
            try:
                import requests
                response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
                data = response.json()
                if "price" in data:
                    price = float(data["price"])
                    logger.info(f"Получена реальная цена {symbol} от Binance: {price}")
                    return price
            except Exception as e:
                logger.warning(f"Не удалось получить реальную цену Binance в тестовом режиме: {e}")
            return 25000.0  # резервная цена
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker["price"])
        except Exception as e:
            logger.error(f"Ошибка получения цены Binance: {e}")
            return 25000.0

    def get_balance(self, coin):
        if TEST_MODE:
            return get_balance(self.name, coin)
        try:
            balance = self.client.get_asset_balance(asset=coin)
            return float(balance["free"]) if balance else 0.0
        except Exception as e:
            logger.error(f"Ошибка получения баланса Binance: {e}")
            return 0.0

    def place_order(self, side, symbol, qty, market_unit=None):
        if TEST_MODE:
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
                result = self.client.order_market(symbol=symbol, side=side.upper(), quantity=qty)
                return result
            except Exception as e:
                logger.error(f"Ошибка размещения ордера Binance: {e}")
                raise

    def init_balances(self):
        """Инициализация балансов при старте"""
        if not TEST_MODE:
            try:
                # Получаем баланс USDT
                usdt_balance = self.get_balance("USDT")
                update_balance(self.name, "USDT", usdt_balance)
                logger.info(f"Binance USDT баланс: {usdt_balance}")
            except Exception as e:
                logger.error(f"Ошибка инициализации баланса Binance: {e}")
