import aiohttp
import asyncio
import json
from loguru import logger
from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED, TEST_MODE, TELEGRAM_BOT_WEBHOOK_URL
from bot.db import get_all_balances, get_profit_statistics, get_trades_summary
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class TelegramBot:
    """Telegram бот для управления и мониторинга торгового бота"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = TELEGRAM_ENABLED and self.bot_token and self.chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.enabled:
            logger.info("Telegram бот отключен")
        else:
            logger.info(f"Telegram бот активирован для чата {self.chat_id}")
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Отправляет сообщение в Telegram"""
        if not self.enabled:
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка отправки сообщения: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Исключение при отправке сообщения: {e}")
            return False
    
    async def process_update(self, update: Dict[str, Any]) -> bool:
        """Обрабатывает входящее обновление от Telegram"""
        try:
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            
            # Проверяем, что сообщение от разрешённого чата
            if str(chat_id) != str(self.chat_id):
                logger.warning(f"Получено сообщение от неразрешённого чата: {chat_id}")
                return False
            
            if not text.startswith("/"):
                return False
            
            command = text.strip().lower()
            logger.info(f"Получена команда: {command}")
            
            # Обрабатываем команды
            if command == "/start" or command == "/help":
                await self.handle_help()
            elif command == "/status":
                await self.handle_status()
            elif command == "/balances":
                await self.handle_balances()
            elif command == "/profit":
                await self.handle_profit()
            elif command == "/strategy":
                await self.handle_strategy()
            elif command == "/summary":
                await self.handle_summary()
            else:
                await self.handle_unknown_command(command)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки обновления: {e}")
            await self.send_message(f"🚨 Ошибка обработки команды: {str(e)}")
            return False
    
    async def handle_help(self):
        """Обработка команды /help"""
        help_text = """
🤖 <b>Торговый бот - Доступные команды:</b>

📊 <b>/status</b> - Статус бота и основная информация
💰 <b>/balances</b> - Текущие балансы по всем монетам
📈 <b>/profit</b> - Статистика прибыли и убытков
🧪 <b>/strategy</b> - Анализ стратегии (прибыль БЕЗ комиссий)
📋 <b>/summary</b> - Краткая сводка по сделкам
❓ <b>/help</b> - Показать это сообщение

🔸 Бот автоматически отправляет уведомления о сделках и ошибках.
🔸 Все команды работают только для авторизованного чата.
        """
        await self.send_message(help_text.strip())
    
    async def handle_status(self):
        """Обработка команды /status"""
        try:
            mode = "🧪 Тестовый режим" if TEST_MODE else "🚀 Боевой режим"
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Получаем общую статистику
            trades_summary = get_trades_summary()
            profit_stats = get_profit_statistics()
            
            # Рассчитываем время работы (примерное)
            import time
            uptime_seconds = int(time.time()) % 86400  # секунды с начала дня
            uptime_hours = uptime_seconds // 3600
            uptime_minutes = (uptime_seconds % 3600) // 60
            
            status_text = f"""
🤖 <b>Статус торгового бота</b>

🔸 <b>Режим:</b> {mode}
🕒 <b>Текущее время:</b> {current_time}
⏱️ <b>Время работы:</b> ~{uptime_hours}ч {uptime_minutes}м
📊 <b>Всего сделок:</b> {trades_summary['total_trades']}
💰 <b>Общая прибыль:</b> ${profit_stats['total_profit']:.4f}
💸 <b>Общие комиссии:</b> ${profit_stats['total_fees']:.4f}
📈 <b>Объём торгов:</b> ${profit_stats['total_volume']:.2f}

✅ <b>Бот работает нормально</b>
            """
            await self.send_message(status_text.strip())
            
        except Exception as e:
            logger.error(f"Ошибка в handle_status: {e}")
            await self.send_message(f"🚨 Ошибка получения статуса: {str(e)}")
    
    async def handle_balances(self):
        """Обработка команды /balances"""
        try:
            balances = get_all_balances()
            
            if not balances:
                await self.send_message("💰 <b>Балансы пусты</b>\n\nНет активных балансов для отображения.")
                return
            
            balance_text = "💰 <b>Текущие балансы:</b>\n\n"
            
            # Группируем по биржам
            bybit_balances = []
            binance_balances = []
            
            for balance in balances:
                exchange = balance['exchange']
                coin = balance['coin']
                amount = balance['amount']
                if exchange == "Bybit":
                    bybit_balances.append((coin, amount))
                elif exchange == "Binance":
                    binance_balances.append((coin, amount))
            
            # Bybit балансы
            if bybit_balances:
                balance_text += "🟦 <b>Bybit:</b>\n"
                for coin, amount in bybit_balances:
                    balance_text += f"   • {coin}: {amount:.6f}\n"
                balance_text += "\n"
            
            # Binance балансы
            if binance_balances:
                balance_text += "🟨 <b>Binance:</b>\n"
                for coin, amount in binance_balances:
                    balance_text += f"   • {coin}: {amount:.6f}\n"
            
            await self.send_message(balance_text.strip())
            
        except Exception as e:
            logger.error(f"Ошибка в handle_balances: {e}")
            await self.send_message(f"🚨 Ошибка получения балансов: {str(e)}")
    
    async def handle_profit(self):
        """Обработка команды /profit"""
        try:
            stats = get_profit_statistics()
            
            # Определяем эмодзи для прибыли
            profit_emoji = "💚" if stats['total_profit'] > 0 else "❤️" if stats['total_profit'] < 0 else "💛"
            
            profit_text = f"""
📈 <b>Статистика прибыли:</b>

{profit_emoji} <b>Общая прибыль:</b> ${stats['total_profit']:.4f}
📊 <b>Средняя прибыль:</b> ${stats['avg_profit']:.4f}
🎯 <b>Процент успеха:</b> {stats['win_rate']:.1f}%

✅ <b>Прибыльных сделок:</b> {stats['profitable_trades']}
❌ <b>Убыточных сделок:</b> {stats['losing_trades']}
📋 <b>Всего сделок с P&L:</b> {stats['total_trades_with_profit']}

🏆 <b>Лучшая сделка:</b> ${stats['best_trade']:.4f}
📉 <b>Худшая сделка:</b> ${stats['worst_trade']:.4f}

💸 <b>Общие комиссии:</b> ${stats['total_fees']:.4f}
📊 <b>Объём торгов:</b> ${stats['total_volume']:.2f}
            """
            
            await self.send_message(profit_text.strip())
            
        except Exception as e:
            logger.error(f"Ошибка в handle_profit: {e}")
            await self.send_message(f"🚨 Ошибка получения статистики прибыли: {str(e)}")
    
    async def handle_strategy(self):
        """Обработка команды /strategy - анализ стратегии БЕЗ комиссий"""
        try:
            from bot.db import get_profit_statistics_no_fees, get_profit_statistics
            
            # Получаем статистику БЕЗ комиссий
            stats_no_fees = get_profit_statistics_no_fees()
            # Получаем обычную статистику для сравнения
            stats_with_fees = get_profit_statistics()
            
            # Эмодзи для прибыли БЕЗ комиссий
            profit_emoji_no_fees = "💚" if stats_no_fees['total_profit_no_fees'] > 0 else "❤️" if stats_no_fees['total_profit_no_fees'] < 0 else "💛"
            
            strategy_text = f"""
🧪 <b>Анализ стратегии (БЕЗ комиссий):</b>

{profit_emoji_no_fees} <b>Общая прибыль БЕЗ комиссий:</b> ${stats_no_fees['total_profit_no_fees']:.4f}
📊 <b>Средняя прибыль БЕЗ комиссий:</b> ${stats_no_fees['avg_profit_no_fees']:.4f}
🎯 <b>Процент успеха БЕЗ комиссий:</b> {stats_no_fees['win_rate_no_fees']:.1f}%

✅ <b>Прибыльных сделок:</b> {stats_no_fees['profitable_trades_no_fees']}
❌ <b>Убыточных сделок:</b> {stats_no_fees['losing_trades_no_fees']}
📋 <b>Всего сделок:</b> {stats_no_fees['total_trades_with_profit_no_fees']}

🏆 <b>Лучшая сделка БЕЗ комиссий:</b> ${stats_no_fees['best_trade_no_fees']:.4f}
📉 <b>Худшая сделка БЕЗ комиссий:</b> ${stats_no_fees['worst_trade_no_fees']:.4f}

<b>📈 Сравнение с учетом комиссий:</b>
• БЕЗ комиссий: ${stats_no_fees['total_profit_no_fees']:.4f}
• С комиссиями: ${stats_with_fees['total_profit']:.4f}
• Потери на комиссиях: ${stats_with_fees['total_fees']:.4f}

💡 <b>Вывод:</b> {'Стратегия прибыльна, проблема в комиссиях' if stats_no_fees['total_profit_no_fees'] > 0 > stats_with_fees['total_profit'] else 'Стратегия работает хорошо' if stats_no_fees['total_profit_no_fees'] > 0 else 'Стратегия требует доработки'}
            """
            
            await self.send_message(strategy_text.strip())
            
        except Exception as e:
            logger.error(f"Ошибка в handle_strategy: {e}")
            await self.send_message(f"🚨 Ошибка анализа стратегии: {str(e)}")
    
    async def handle_summary(self):
        """Обработка команды /summary"""
        try:
            summary = get_trades_summary()
            
            summary_text = f"📋 <b>Краткая сводка:</b>\n\n"
            summary_text += f"📊 <b>Всего сделок:</b> {summary['total_trades']}\n\n"
            
            if summary['recent_trades']:
                summary_text += "🕒 <b>Последние 5 сделок:</b>\n"
                for trade in summary['recent_trades']:
                    timestamp = trade['timestamp']
                    exchange = trade['exchange']
                    side = trade['side']
                    symbol = trade['symbol']
                    price = trade['price']
                    qty = trade['qty']
                    amount_usdt = trade['amount_usdt']
                    profit = trade['profit']
                    
                    # Форматируем время
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime("%m-%d %H:%M")
                    except:
                        time_str = timestamp[:16]
                    
                    # Эмодзи для типа сделки
                    side_emoji = "🟢" if side == "buy" else "🔴"
                    
                    # Прибыль (только для продаж)
                    profit_str = ""
                    if side == "sell" and profit is not None:
                        profit_emoji = "💚" if profit > 0 else "❤️"
                        profit_str = f" {profit_emoji}${profit:.3f}"
                    
                    summary_text += f"{side_emoji} {time_str} {exchange} {symbol} ${amount_usdt:.2f}{profit_str}\n"
            else:
                summary_text += "📭 Нет сделок для отображения"
            
            await self.send_message(summary_text.strip())
            
        except Exception as e:
            logger.error(f"Ошибка в handle_summary: {e}")
            await self.send_message(f"🚨 Ошибка получения сводки: {str(e)}")
    
    async def handle_unknown_command(self, command: str):
        """Обработка неизвестной команды"""
        unknown_text = f"""
❓ <b>Неизвестная команда:</b> {command}

Используйте /help для просмотра доступных команд.
        """
        await self.send_message(unknown_text.strip())
    
    async def setup_webhook(self, webhook_url: str) -> bool:
        """Настройка webhook для бота"""
        if not self.enabled:
            return False
        
        url = f"{self.base_url}/setWebhook"
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            logger.info(f"Telegram webhook настроен: {webhook_url}")
                            return True
                        else:
                            logger.error(f"Ошибка настройки webhook: {result}")
                            return False
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка HTTP при настройке webhook: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Исключение при настройке webhook: {e}")
            return False
    
    async def remove_webhook(self) -> bool:
        """Удаление webhook"""
        if not self.enabled:
            return False
        
        url = f"{self.base_url}/deleteWebhook"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            logger.info("Telegram webhook удалён")
                            return True
                        else:
                            logger.error(f"Ошибка удаления webhook: {result}")
                            return False
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка HTTP при удалении webhook: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Исключение при удалении webhook: {e}")
            return False


# Глобальный экземпляр бота
telegram_bot = TelegramBot()


# Функции-обёртки
async def process_telegram_update(update: Dict[str, Any]) -> bool:
    """Обрабатывает обновление от Telegram"""
    return await telegram_bot.process_update(update)


async def send_telegram_message(text: str) -> bool:
    """Отправляет сообщение в Telegram"""
    return await telegram_bot.send_message(text)


async def setup_telegram_webhook() -> bool:
    """Настройка Telegram webhook (если URL указан)"""
    if TELEGRAM_BOT_WEBHOOK_URL:
        return await telegram_bot.setup_webhook(TELEGRAM_BOT_WEBHOOK_URL)
    return False


async def remove_telegram_webhook() -> bool:
    """Удаление Telegram webhook"""
    return await telegram_bot.remove_webhook()
