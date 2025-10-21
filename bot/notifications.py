"""
Модуль для отправки уведомлений
Поддерживает Telegram уведомления
"""

import aiohttp
from loguru import logger
from typing import Dict, Any
from datetime import datetime

from .strategy import TradingSignal, SignalType
from .trading_engine import Trade, Position


class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self, config: Dict):
        """
        Инициализация менеджера уведомлений
        
        Args:
            config: Конфигурация из config.yaml
        """
        self.config = config
        self.notifications_config = config.get('notifications', {})
        
        # Telegram настройки
        self.telegram_enabled = self.notifications_config.get('telegram_enabled', False)
        self.telegram_token = self.notifications_config.get('telegram_token', '')
        self.telegram_chat_id = self.notifications_config.get('telegram_chat_id', '')
        
        # Настройки уведомлений
        self.notify_signals = self.notifications_config.get('notify_signals', True)
        self.notify_trades = self.notifications_config.get('notify_trades', True)
        self.notify_errors = self.notifications_config.get('notify_errors', True)
        
        # URL для Telegram API
        if self.telegram_enabled and self.telegram_token:
            self.telegram_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        else:
            self.telegram_url = None
        
        logger.info(f"Менеджер уведомлений инициализирован: Telegram {'включен' if self.telegram_enabled else 'отключен'}")
    
    async def send_signal_notification(self, signal: TradingSignal):
        """Отправка уведомления о торговом сигнале"""
        if not self.notify_signals or not self.telegram_enabled:
            return
        
        try:
            # Формируем сообщение
            emoji = "🟢" if signal.signal_type == SignalType.BUY else "🔴" if signal.signal_type == SignalType.SELL else "⚪"
            signal_text = signal.signal_type.value
            
            message = f"{emoji} *Торговый сигнал*\n\n"
            message += f"📊 *Символ:* {signal.symbol}\n"
            message += f"📈 *Сигнал:* {signal_text}\n"
            message += f"💰 *Цена:* {signal.price:.4f}\n"
            message += f"🎯 *Уверенность:* {signal.confidence:.2%}\n"
            message += f"⏰ *Время:* {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"📝 *Причина:* {signal.reason}\n"
            
            # Добавляем информацию о фильтрах
            if signal.filters_passed:
                message += "\n🔍 *Фильтры:*\n"
                for filter_name, passed in signal.filters_passed.items():
                    status = "✅" if passed else "❌"
                    message += f"{status} {filter_name.upper()}\n"
            
            # Добавляем данные индикаторов
            if signal.indicators_data:
                message += "\n📊 *Индикаторы:*\n"
                for indicator, value in signal.indicators_data.items():
                    if value is not None:
                        message += f"• {indicator}: {value:.4f}\n"
            
            await self._send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о сигнале: {e}")
    
    async def send_trade_notification(self, trade: Trade):
        """Отправка уведомления о сделке"""
        if not self.notify_trades or not self.telegram_enabled:
            return
        
        try:
            # Формируем сообщение
            emoji = "🟢" if trade.side == 'buy' else "🔴"
            side_text = "Покупка" if trade.side == 'buy' else "Продажа"
            
            message = f"{emoji} *Сделка исполнена*\n\n"
            message += f"📊 *Символ:* {trade.symbol}\n"
            message += f"📈 *Тип:* {side_text}\n"
            message += f"💰 *Количество:* {trade.amount:.6f}\n"
            message += f"💵 *Цена:* {trade.price:.4f}\n"
            message += f"💸 *Сумма:* {trade.amount * trade.price:.2f} USDT\n"
            message += f"⏰ *Время:* {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"🏢 *Биржа:* {trade.exchange.upper()}\n"
            
            # Добавляем PnL для продаж
            if trade.side == 'sell' and trade.pnl is not None:
                pnl_emoji = "📈" if trade.pnl > 0 else "📉"
                message += f"{pnl_emoji} *PnL:* {trade.pnl:.4f} USDT\n"
            
            # Добавляем комиссию
            if trade.fee > 0:
                message += f"💳 *Комиссия:* {trade.fee:.4f}\n"
            
            await self._send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о сделке: {e}")
    
    async def send_error_notification(self, error: str, context: str = ""):
        """Отправка уведомления об ошибке"""
        if not self.notify_errors or not self.telegram_enabled:
            return
        
        try:
            message = f"🚨 *Ошибка бота*\n\n"
            message += f"❌ *Ошибка:* {error}\n"
            if context:
                message += f"📍 *Контекст:* {context}\n"
            message += f"⏰ *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            await self._send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления об ошибке: {e}")
    
    async def send_status_notification(self, status_data: Dict[str, Any]):
        """Отправка уведомления о статусе бота"""
        if not self.telegram_enabled:
            return
        
        try:
            message = "📊 *Статус бота*\n\n"
            message += f"⏰ *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Добавляем данные статуса
            for key, value in status_data.items():
                if isinstance(value, (int, float)):
                    if 'balance' in key.lower() or 'pnl' in key.lower():
                        message += f"💰 *{key}:* {value:.4f}\n"
                    elif 'rate' in key.lower() or 'percent' in key.lower():
                        message += f"📈 *{key}:* {value:.2f}%\n"
                    else:
                        message += f"📊 *{key}:* {value}\n"
                else:
                    message += f"📋 *{key}:* {value}\n"
            
            await self._send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о статусе: {e}")
    
    async def send_daily_report(self, stats: Dict[str, Any]):
        """Отправка ежедневного отчета"""
        if not self.telegram_enabled:
            return
        
        try:
            message = f"📈 *Ежедневный отчет*\n\n"
            message += f"📅 *Дата:* {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            # Статистика торговли
            if 'trading_stats' in stats:
                trading = stats['trading_stats']
                message += f"📊 *Торговля:*\n"
                message += f"• Сделок: {trading.get('total_trades', 0)}\n"
                message += f"• PnL: {trading.get('total_pnl', 0):.4f} USDT\n"
                message += f"• Винрейт: {trading.get('win_rate', 0):.1f}%\n"
                message += f"• Средняя сделка: {trading.get('avg_trade', 0):.4f} USDT\n\n"
            
            # Статистика стратегии
            if 'strategy_stats' in stats:
                strategy = stats['strategy_stats']
                message += f"🎯 *Стратегия:*\n"
                message += f"• Сигналов: {strategy.get('total_signals', 0)}\n"
                message += f"• Покупок: {strategy.get('buy_signals', 0)}\n"
                message += f"• Продаж: {strategy.get('sell_signals', 0)}\n"
                message += f"• Средняя уверенность: {strategy.get('avg_confidence', 0):.2%}\n\n"
            
            # Баланс
            if 'balance' in stats:
                balance = stats['balance']
                message += f"💰 *Баланс:*\n"
                for currency, amount in balance.items():
                    if amount > 0:
                        message += f"• {currency}: {amount:.4f}\n"
            
            await self._send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка отправки ежедневного отчета: {e}")
    
    async def send_position_update(self, position: Position):
        """Отправка уведомления об обновлении позиции"""
        if not self.telegram_enabled:
            return
        
        try:
            pnl_emoji = "📈" if position.unrealized_pnl > 0 else "📉"
            
            message = f"📊 *Обновление позиции*\n\n"
            message += f"📈 *Символ:* {position.symbol}\n"
            message += f"📊 *Тип:* {position.side.upper()}\n"
            message += f"💰 *Количество:* {position.amount:.6f}\n"
            message += f"💵 *Цена входа:* {position.entry_price:.4f}\n"
            message += f"📈 *Текущая цена:* {position.current_price:.4f}\n"
            message += f"{pnl_emoji} *Нереализованный PnL:* {position.unrealized_pnl:.4f} USDT\n"
            message += f"⏰ *Время входа:* {position.entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            await self._send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о позиции: {e}")
    
    async def _send_telegram_message(self, message: str):
        """Отправка сообщения в Telegram"""
        if not self.telegram_url or not self.telegram_chat_id:
            return
        
        try:
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.telegram_url, json=payload) as response:
                    if response.status == 200:
                        logger.debug("Telegram сообщение отправлено успешно")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка отправки Telegram сообщения: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Ошибка отправки Telegram сообщения: {e}")
    
    def test_telegram_connection(self) -> bool:
        """Тестирование подключения к Telegram"""
        if not self.telegram_enabled or not self.telegram_token or not self.telegram_chat_id:
            return False
        
        try:
            import requests
            
            test_url = f"https://api.telegram.org/bot{self.telegram_token}/getMe"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logger.info(f"Telegram подключение успешно: @{bot_info['result']['username']}")
                    return True
            
            logger.error(f"Ошибка подключения к Telegram: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка тестирования Telegram: {e}")
            return False
    
    async def send_test_message(self):
        """Отправка тестового сообщения"""
        if not self.telegram_enabled:
            return False
        
        try:
            message = "🤖 *Тестовое сообщение*\n\n"
            message += "Бот успешно подключен к Telegram!\n"
            message += f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await self._send_telegram_message(message)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки тестового сообщения: {e}")
            return False
    
    def update_config(self, new_config: Dict):
        """Обновление конфигурации уведомлений"""
        self.config = new_config
        self.notifications_config = new_config.get('notifications', {})
        
        # Обновляем настройки
        self.telegram_enabled = self.notifications_config.get('telegram_enabled', False)
        self.telegram_token = self.notifications_config.get('telegram_token', '')
        self.telegram_chat_id = self.notifications_config.get('telegram_chat_id', '')
        
        # Обновляем URL
        if self.telegram_enabled and self.telegram_token:
            self.telegram_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        else:
            self.telegram_url = None
        
        logger.info("Конфигурация уведомлений обновлена")
