import aiohttp
import asyncio
from loguru import logger
from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
from typing import Optional, Dict, Any


class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = TELEGRAM_ENABLED and self.bot_token and self.chat_id
        
        if not self.enabled:
            logger.info("Telegram уведомления отключены")
        else:
            logger.info(f"Telegram уведомления включены для чата {self.chat_id}")
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Отправляет сообщение в Telegram"""
        if not self.enabled:
            logger.debug("Telegram уведомления отключены, сообщение не отправлено")
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.debug("Telegram сообщение отправлено успешно")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка отправки Telegram сообщения: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Исключение при отправке Telegram сообщения: {e}")
            return False
    
    def format_trade_message(self, trade_data: Dict[str, Any]) -> str:
        """Форматирует сообщение о сделке"""
        side_emoji = "🟢" if trade_data["side"] == "buy" else "🔴"
        side_text = "Покупка" if trade_data["side"] == "buy" else "Продажа"
        
        message = f"""
{side_emoji} <b>{side_text} выполнена!</b>

📊 <b>Биржа:</b> {trade_data["exchange"]}
💰 <b>Пара:</b> {trade_data["symbol"]}
💵 <b>Цена:</b> ${trade_data["price"]:.6f}
📦 <b>Количество:</b> {trade_data["qty"]:.6f}
💸 <b>Сумма:</b> ${trade_data["amount_usdt"]:.2f}
🔸 <b>Комиссия:</b> ${trade_data["fee"]:.4f}
💳 <b>Баланс после:</b> ${trade_data["balance_after"]:.2f}
"""
        
        if trade_data.get("profit") is not None:
            profit_emoji = "💚" if trade_data["profit"] > 0 else "❤️"
            message += f"{profit_emoji} <b>Прибыль:</b> ${trade_data['profit']:.4f}\n"
        
        message += f"\n🆔 <b>ID:</b> {trade_data['request_id']}"
        
        return message.strip()
    
    def format_error_message(self, error: str, context: str = "") -> str:
        """Форматирует сообщение об ошибке"""
        message = "🚨 <b>Ошибка в торговом боте!</b>\n\n"
        
        if context:
            message += f"📍 <b>Контекст:</b> {context}\n"
        
        message += f"❌ <b>Ошибка:</b> {error}"
        
        return message
    
    def format_status_message(self, status: str, details: Dict[str, Any] = None) -> str:
        """Форматирует статусное сообщение"""
        message = f"📋 <b>Статус бота:</b> {status}\n\n"
        
        if details:
            for key, value in details.items():
                message += f"🔸 <b>{key}:</b> {value}\n"
        
        return message.strip()
    
    async def notify_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Отправляет уведомление о сделке"""
        message = self.format_trade_message(trade_data)
        return await self.send_message(message)
    
    async def notify_error(self, error: str, context: str = "") -> bool:
        """Отправляет уведомление об ошибке"""
        message = self.format_error_message(error, context)
        return await self.send_message(message)
    
    async def notify_status(self, status: str, details: Dict[str, Any] = None) -> bool:
        """Отправляет статусное уведомление"""
        message = self.format_status_message(status, details)
        return await self.send_message(message)


# Глобальный экземпляр уведомителя
telegram_notifier = TelegramNotifier()


# Функции-обёртки для удобства использования
async def notify_trade(trade_data: Dict[str, Any]) -> bool:
    """Отправляет уведомление о сделке"""
    return await telegram_notifier.notify_trade(trade_data)


async def notify_error(error: str, context: str = "") -> bool:
    """Отправляет уведомление об ошибке"""
    return await telegram_notifier.notify_error(error, context)


async def notify_status(status: str, details: Dict[str, Any] = None) -> bool:
    """Отправляет статусное уведомление"""
    return await telegram_notifier.notify_status(status, details)
