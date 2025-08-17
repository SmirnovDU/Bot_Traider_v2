"""
Расчет портфеля и общего баланса в USDT
"""

from loguru import logger
from bot.db import get_all_balances
from bot.exchange_selector import ExchangeSelector


class PortfolioCalculator:
    def __init__(self):
        self.exchange_selector = ExchangeSelector()
    
    def get_total_portfolio_usdt(self):
        """Получить общий баланс портфеля в USDT"""
        try:
            balances = get_all_balances()
            total_usdt = 0.0
            breakdown = {
                "Bybit": {"USDT": 0.0, "coins_usdt": 0.0, "total": 0.0},
                "Binance": {"USDT": 0.0, "coins_usdt": 0.0, "total": 0.0}
            }
            
            for balance in balances:
                exchange_name = balance['exchange']
                coin = balance['coin']
                amount = balance['amount']
                
                if coin == "USDT":
                    # USDT считаем 1:1
                    breakdown[exchange_name]["USDT"] = amount
                    total_usdt += amount
                else:
                    # Для других монет получаем курс продажи
                    try:
                        exchange = self.exchange_selector.get_exchange_by_name(exchange_name.lower())
                        symbol = f"{coin}USDT"
                        price = exchange.get_last_price(symbol)
                        
                        coin_usdt_value = amount * price
                        breakdown[exchange_name]["coins_usdt"] += coin_usdt_value
                        total_usdt += coin_usdt_value
                        
                        logger.debug(f"💱 {coin}: {amount:.6f} × ${price:.6f} = ${coin_usdt_value:.2f} ({exchange_name})")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Не удалось получить курс {coin} на {exchange_name}: {e}")
            
            # Подсчитываем итоги по биржам
            for exchange_name in breakdown:
                breakdown[exchange_name]["total"] = breakdown[exchange_name]["USDT"] + breakdown[exchange_name]["coins_usdt"]
            
            logger.info(f"💰 Общий портфель: ${total_usdt:.2f}")
            
            return {
                "total_usdt": total_usdt,
                "breakdown": breakdown
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка расчета портфеля: {e}")
            return {
                "total_usdt": 0.0,
                "breakdown": {
                    "Bybit": {"USDT": 0.0, "coins_usdt": 0.0, "total": 0.0},
                    "Binance": {"USDT": 0.0, "coins_usdt": 0.0, "total": 0.0}
                }
            }
    
    def format_portfolio_text(self, portfolio):
        """Форматировать текст портфеля для Telegram"""
        breakdown = portfolio['breakdown']
        total_usdt = portfolio['total_usdt']
        
        text = f"\n💼 <b>Общий портфель: ${total_usdt:.2f}</b>\n\n"
        
        for exchange_name, data in breakdown.items():
            if data['total'] > 0:
                emoji = "🟦" if exchange_name == "Bybit" else "🟨"
                text += f"{emoji} <b>{exchange_name}:</b> ${data['total']:.2f}\n"
                if data['USDT'] > 0:
                    text += f"   💵 USDT: ${data['USDT']:.2f}\n"
                if data['coins_usdt'] > 0:
                    text += f"   🪙 Монеты: ${data['coins_usdt']:.2f}\n"
        
        return text


# Глобальный экземпляр для использования в других модулях
portfolio_calculator = PortfolioCalculator()
