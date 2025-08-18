"""
Модуль для массовых операций с монетами
"""

import asyncio
from loguru import logger
from datetime import datetime, timezone
from bot.db import get_all_balances, save_trade, update_balance
from bot.exchange_selector import ExchangeSelector
from bot.utils import generate_request_id, calculate_fee_for_sell
from bot.config import TEST_MODE

class MassOperations:
    """Класс для выполнения массовых операций"""
    
    def __init__(self):
        self.exchange_selector = ExchangeSelector()
    
    async def sell_all_coins(self, exchange_name: str = None) -> dict:
        """
        Продать все монеты на указанной бирже или на всех биржах
        
        Args:
            exchange_name: Название биржи ("bybit", "binance") или None для всех бирж
            
        Returns:
            dict: Результат операции
        """
        try:
            balances = get_all_balances()
            if not balances:
                return {
                    "success": True,
                    "message": "Нет монет для продажи",
                    "trades": [],
                    "total_profit": 0.0
                }
            
            # Фильтруем балансы по бирже, если указана
            if exchange_name:
                balances = [b for b in balances if b['exchange'].lower() == exchange_name.lower()]
                if not balances:
                    return {
                        "success": True,
                        "message": f"Нет монет для продажи на {exchange_name}",
                        "trades": [],
                        "total_profit": 0.0
                    }
            
            # Исключаем USDT из продажи
            balances = [b for b in balances if b['coin'] != 'USDT']
            
            if not balances:
                return {
                    "success": True,
                    "message": "Нет монет для продажи (только USDT)",
                    "trades": [],
                    "total_profit": 0.0
                }
            
            logger.info(f"Начинаем массовую продажу {len(balances)} монет")
            
            trades = []
            total_profit = 0.0
            successful_trades = 0
            failed_trades = 0
            
            for balance in balances:
                try:
                    result = await self._sell_single_coin(balance)
                    if result['success']:
                        trades.append(result)
                        total_profit += result.get('profit', 0.0)
                        successful_trades += 1
                    else:
                        failed_trades += 1
                        logger.error(f"Ошибка продажи {balance['coin']}: {result['error']}")
                    
                    # Небольшая задержка между операциями
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    failed_trades += 1
                    logger.error(f"Исключение при продаже {balance['coin']}: {e}")
            
            message = f"Массовая продажа завершена: {successful_trades} успешно, {failed_trades} неудачно"
            if exchange_name:
                message += f" на {exchange_name}"
            
            return {
                "success": True,
                "message": message,
                "trades": trades,
                "total_profit": total_profit,
                "successful_trades": successful_trades,
                "failed_trades": failed_trades
            }
            
        except Exception as e:
            logger.error(f"Ошибка массовой продажи: {e}")
            return {
                "success": False,
                "error": str(e),
                "trades": [],
                "total_profit": 0.0
            }
    
    async def _sell_single_coin(self, balance: dict) -> dict:
        """
        Продать одну монету
        
        Args:
            balance: Словарь с информацией о балансе
            
        Returns:
            dict: Результат операции
        """
        try:
            exchange_name = balance['exchange']
            coin = balance['coin']
            amount = balance['amount']
            
            if amount <= 0:
                return {
                    "success": False,
                    "error": f"Нулевой баланс {coin}",
                    "coin": coin,
                    "exchange": exchange_name
                }
            
            symbol = f"{coin}USDT"
            qty = amount
            
            # Проверяем минимальное количество
            if qty <= 0:
                return {
                    "success": False,
                    "error": f"Слишком малое количество {coin}",
                    "coin": coin,
                    "exchange": exchange_name,
                    "qty": qty
                }
            
            # Генерируем request_id
            request_id = generate_request_id(symbol, "sell")
            
            if TEST_MODE:
                # ТЕСТОВЫЙ РЕЖИМ - получаем реальную цену с биржи, но не делаем реальные сделки
                logger.info(f"🧪 ТЕСТ: Продаём {qty} {coin} на {exchange_name}")
                
                # Получаем биржу для запроса цены
                exchange = self.exchange_selector.get_exchange_by_name(exchange_name)
                
                # Получаем реальную цену с биржи
                try:
                    price = exchange.get_last_price(symbol)
                    logger.info(f"🧪 ТЕСТ: Получена цена {coin} с {exchange_name}: ${price}")
                except Exception as e:
                    logger.warning(f"🧪 ТЕСТ: Не удалось получить цену {coin} с {exchange_name}: {e}")
                    # Используем фиксированную цену как fallback
                    if coin == "BTC":
                        price = 45000.0
                    elif coin == "ETH":
                        price = 3000.0
                    elif coin == "ADA":
                        price = 0.5
                    elif coin == "DOT":
                        price = 7.0
                    else:
                        price = 1.0
                    logger.info(f"🧪 ТЕСТ: Используем фиксированную цену для {coin}: ${price}")
                
                # Рассчитываем комиссию (0.1% от суммы)
                fee = (qty * price) * 0.001
                
                # Получаем текущий баланс USDT из БД
                from bot.db import get_balance
                current_usdt_balance = get_balance(exchange_name, "USDT")
                
                # Рассчитываем новый баланс USDT (реальная цена с биржи)
                new_usdt_balance = current_usdt_balance + (qty * price) - fee
                
                # Рассчитываем прибыль по реальной цене с биржи
                profit = (qty * price) - fee
                profit_no_fees = qty * price  # Прибыль без комиссий
                
                # Сохраняем сделку
                trade_data = {
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "exchange": exchange_name,
                    "side": "sell",
                    "symbol": symbol,
                    "price": price,
                    "qty": qty,
                    "amount_usdt": qty * price,
                    "fee": fee,
                    "profit": profit,
                    "profit_no_fees": profit_no_fees,
                    "balance_after": new_usdt_balance,
                    "note": f"Массовая продажа (ТЕСТОВЫЙ РЕЖИМ) - цена с {exchange_name}"
                }
                save_trade(trade_data)
                
                # Обновляем баланс в БД
                update_balance(exchange_name, coin, 0.0)  # Обнуляем баланс монеты
                update_balance(exchange_name, "USDT", new_usdt_balance)  # Обновляем USDT
                
                logger.info(f"🧪 ТЕСТ: Продажа {coin} завершена. Прибыль: ${profit:.4f}")
                
                return {
                    "success": True,
                    "coin": coin,
                    "exchange": exchange_name,
                    "qty": qty,
                    "price": price,
                    "profit": profit,
                    "fee": fee,
                    "request_id": request_id
                }
            else:
                # БОЕВОЙ РЕЖИМ - работаем с реальными биржами
                exchange = self.exchange_selector.get_exchange_by_name(exchange_name)
                
                # Получаем текущую цену
                price = exchange.get_last_price(symbol)
                
                logger.info(f"Продаём {qty} {coin} по цене {price} на {exchange_name}")
                
                # Выполняем продажу
                result = exchange.place_order(symbol, "sell", qty, price)
                
                if result.get("success"):
                    # Рассчитываем комиссию и прибыль
                    fee = calculate_fee_for_sell(qty, price, result.get("balance_after", 0))
                    
                    # Получаем баланс после операции
                    balance_after = exchange.get_balance("USDT")
                    
                    # Рассчитываем прибыль (для массовой продажи считаем как продажу по текущей цене)
                    profit = (qty * price) - fee
                    profit_no_fees = qty * price  # Прибыль без комиссий
                    
                    # Сохраняем сделку
                    trade_data = {
                        "request_id": request_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "exchange": exchange_name,
                        "side": "sell",
                        "symbol": symbol,
                        "price": price,
                        "qty": qty,
                        "amount_usdt": qty * price,
                        "fee": fee,
                        "profit": profit,
                        "profit_no_fees": profit_no_fees,
                        "balance_after": balance_after,
                        "note": f"Массовая продажа - {result.get('note', '')}"
                    }
                    save_trade(trade_data)
                    
                    # Обновляем баланс в БД
                    update_balance(exchange_name, coin, 0.0)  # Обнуляем баланс монеты
                    update_balance(exchange_name, "USDT", balance_after)  # Обновляем USDT
                    
                    return {
                        "success": True,
                        "coin": coin,
                        "exchange": exchange_name,
                        "qty": qty,
                        "price": price,
                        "profit": profit,
                        "fee": fee,
                        "request_id": request_id
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Неизвестная ошибка"),
                        "coin": coin,
                        "exchange": exchange_name,
                        "qty": qty,
                        "price": price
                    }
                
        except Exception as e:
            logger.error(f"Ошибка продажи {balance.get('coin', 'unknown')}: {e}")
            return {
                "success": False,
                "error": str(e),
                "coin": balance.get('coin', 'unknown'),
                "exchange": balance.get('exchange', 'unknown')
            }


# Глобальный экземпляр
mass_operations = MassOperations()


# Функции-обёртки для удобства
async def sell_all_coins(exchange_name: str = None) -> dict:
    """Продать все монеты на указанной бирже или на всех биржах"""
    return await mass_operations.sell_all_coins(exchange_name)


async def sell_all_binance() -> dict:
    """Продать все монеты на Binance"""
    return await mass_operations.sell_all_coins("binance")


async def sell_all_bybit() -> dict:
    """Продать все монеты на Bybit"""
    return await mass_operations.sell_all_coins("bybit")
