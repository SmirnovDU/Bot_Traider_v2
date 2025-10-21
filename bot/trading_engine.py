"""
Торговый движок для исполнения ордеров
Поддерживает симуляцию и реальную торговлю
"""

import ccxt
from loguru import logger
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os

from .data_fetcher import DataFetcher
from .strategy import TradingSignal, SignalType


@dataclass
class Trade:
    """Информация о сделке"""
    id: str
    symbol: str
    side: str  # 'buy' или 'sell'
    amount: float
    price: float
    timestamp: datetime
    exchange: str
    order_id: Optional[str] = None
    status: str = 'filled'  # filled, pending, cancelled
    fee: float = 0.0
    pnl: Optional[float] = None  # Прибыль/убыток


@dataclass
class Position:
    """Информация о позиции"""
    symbol: str
    side: str  # 'long' или 'short'
    amount: float
    entry_price: float
    entry_time: datetime
    current_price: float
    unrealized_pnl: float
    exchange: str


class TradingEngine:
    """Торговый движок для исполнения ордеров"""
    
    def __init__(self, config: Dict, data_fetcher: DataFetcher):
        """
        Инициализация торгового движка
        
        Args:
            config: Конфигурация из config.yaml
            data_fetcher: Объект для получения данных
        """
        self.config = config
        self.data_fetcher = data_fetcher
        
        # Настройки торговли
        trading_config = config.get('trading', {})
        self.symbol = trading_config.get('symbol', 'BTC/USDT')
        self.trade_amount = trading_config.get('trade_amount', 5)
        self.trade_amount_type = trading_config.get('trade_amount_type', 'fixed')
        self.initial_capital = trading_config.get('initial_capital', 1000)
        self.simulation_mode = self._str_to_bool(trading_config.get('simulation_mode', True))
        self.default_exchange = trading_config.get('default_exchange', 'binance')
        
        # Состояние
        self.trades: List[Trade] = []
        self.positions: Dict[str, Position] = {}
        self.balance = {'USDT': self.initial_capital}
        
        # Инициализация биржи для реальной торговли
        if not self.simulation_mode:
            self._init_real_exchange()
        
        # Загрузка истории сделок
        self._load_trade_history()
        
        logger.info(f"Торговый движок инициализирован: {'Симуляция' if self.simulation_mode else 'Реальная торговля'}")
    
    def _init_real_exchange(self):
        """Инициализация реальной биржи"""
        try:
            exchanges_config = self.config.get('exchanges', {})
            exchange_config = exchanges_config.get(self.default_exchange, {})
            
            if not exchange_config.get('enabled', False):
                raise ValueError(f"Биржа {self.default_exchange} не включена")
            
            # Создаем объект биржи
            if self.default_exchange == 'binance':
                self.exchange = ccxt.binance({
                    'apiKey': exchange_config.get('api_key', ''),
                    'secret': exchange_config.get('secret_key', ''),
                    'sandbox': exchange_config.get('testnet', False),
                    'options': {'defaultType': 'spot'}
                })
            elif self.default_exchange == 'bybit':
                self.exchange = ccxt.bybit({
                    'apiKey': exchange_config.get('api_key', ''),
                    'secret': exchange_config.get('secret_key', ''),
                    'sandbox': exchange_config.get('testnet', False),
                    'options': {'defaultType': 'spot'}
                })
            else:
                raise ValueError(f"Неподдерживаемая биржа: {self.default_exchange}")
            
            logger.info(f"Инициализирована реальная биржа: {self.default_exchange}")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации реальной биржи: {e}")
            raise
    
    def execute_signal(self, signal: TradingSignal) -> bool:
        """
        Исполнение торгового сигнала
        
        Args:
            signal: Торговый сигнал
            
        Returns:
            True если ордер исполнен успешно
        """
        try:
            if signal.signal_type == SignalType.BUY:
                return self._execute_buy_order(signal)
            elif signal.signal_type == SignalType.SELL:
                return self._execute_sell_order(signal)
            else:
                return True  # HOLD не требует действий
                
        except Exception as e:
            logger.error(f"Ошибка исполнения сигнала: {e}")
            return False
    
    def _execute_buy_order(self, signal: TradingSignal) -> bool:
        """Исполнение ордера на покупку"""
        try:
            # Рассчитываем количество для покупки
            amount = self._calculate_trade_amount(signal.price, 'buy')
            
            if amount <= 0:
                logger.warning("Недостаточно средств для покупки")
                return False
            
            if self.simulation_mode:
                return self._simulate_buy_order(signal, amount)
            else:
                return self._real_buy_order(signal, amount)
                
        except Exception as e:
            logger.error(f"Ошибка исполнения ордера покупки: {e}")
            return False
    
    def _execute_sell_order(self, signal: TradingSignal) -> bool:
        """Исполнение ордера на продажу"""
        try:
            # Получаем текущую позицию
            position = self.positions.get(self.symbol)
            if not position or position.side != 'long':
                logger.warning("Нет длинной позиции для продажи")
                return False
            
            amount = position.amount
            
            if self.simulation_mode:
                return self._simulate_sell_order(signal, amount)
            else:
                return self._real_sell_order(signal, amount)
                
        except Exception as e:
            logger.error(f"Ошибка исполнения ордера продажи: {e}")
            return False
    
    def _calculate_trade_amount(self, price: float, side: str) -> float:
        """Расчет количества для торговли"""
        try:
            if self.trade_amount_type == 'fixed':
                # Фиксированная сумма в USDT
                return self.trade_amount / price
            elif self.trade_amount_type == 'percentage':
                # Процент от капитала
                if side == 'buy':
                    available_balance = self.balance.get('USDT', 0)
                    trade_value = available_balance * (self.trade_amount / 100)
                    return trade_value / price
                else:
                    # Для продажи используем всю позицию
                    position = self.positions.get(self.symbol)
                    return position.amount if position else 0
            elif self.trade_amount_type == 'coins':
                # Фиксированное количество монет
                return self.trade_amount
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Ошибка расчета количества: {e}")
            return 0
    
    def _simulate_buy_order(self, signal: TradingSignal, amount: float) -> bool:
        """Симуляция ордера покупки"""
        try:
            # Проверяем баланс
            required_usdt = amount * signal.price
            if self.balance.get('USDT', 0) < required_usdt:
                logger.warning(f"Недостаточно USDT: {self.balance.get('USDT', 0)} < {required_usdt}")
                return False
            
            # Создаем сделку
            trade_id = f"sim_buy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            trade = Trade(
                id=trade_id,
                symbol=signal.symbol,
                side='buy',
                amount=amount,
                price=signal.price,
                timestamp=signal.timestamp,
                exchange=self.default_exchange,
                status='filled'
            )
            
            # Обновляем баланс
            self.balance['USDT'] -= required_usdt
            base_currency = signal.symbol.split('/')[0]
            self.balance[base_currency] = self.balance.get(base_currency, 0) + amount
            
            # Обновляем позицию
            self.positions[signal.symbol] = Position(
                symbol=signal.symbol,
                side='long',
                amount=amount,
                entry_price=signal.price,
                entry_time=signal.timestamp,
                current_price=signal.price,
                unrealized_pnl=0.0,
                exchange=self.default_exchange
            )
            
            # Добавляем сделку
            self.trades.append(trade)
            self._save_trade_history()
            
            logger.info(f"[SIM] Куплено {amount:.6f} {signal.symbol} по цене {signal.price}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка симуляции покупки: {e}")
            return False
    
    def _simulate_sell_order(self, signal: TradingSignal, amount: float) -> bool:
        """Симуляция ордера продажи"""
        try:
            # Проверяем позицию
            position = self.positions.get(signal.symbol)
            if not position or position.amount < amount:
                logger.warning(f"Недостаточно {signal.symbol} для продажи")
                return False
            
            # Создаем сделку
            trade_id = f"sim_sell_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            trade = Trade(
                id=trade_id,
                symbol=signal.symbol,
                side='sell',
                amount=amount,
                price=signal.price,
                timestamp=signal.timestamp,
                exchange=self.default_exchange,
                status='filled'
            )
            
            # Рассчитываем PnL
            pnl = (signal.price - position.entry_price) * amount
            trade.pnl = pnl
            
            # Обновляем баланс
            received_usdt = amount * signal.price
            self.balance['USDT'] += received_usdt
            base_currency = signal.symbol.split('/')[0]
            self.balance[base_currency] -= amount
            
            # Обновляем или удаляем позицию
            if position.amount == amount:
                del self.positions[signal.symbol]
            else:
                position.amount -= amount
            
            # Добавляем сделку
            self.trades.append(trade)
            self._save_trade_history()
            
            logger.info(f"[SIM] Продано {amount:.6f} {signal.symbol} по цене {signal.price}, PnL: {pnl:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка симуляции продажи: {e}")
            return False
    
    def _real_buy_order(self, signal: TradingSignal, amount: float) -> bool:
        """Реальный ордер покупки"""
        try:
            # Размещаем ордер
            order = self.exchange.create_market_buy_order(signal.symbol, amount)
            
            # Создаем сделку
            trade_id = f"real_buy_{order['id']}"
            trade = Trade(
                id=trade_id,
                symbol=signal.symbol,
                side='buy',
                amount=amount,
                price=signal.price,
                timestamp=signal.timestamp,
                exchange=self.default_exchange,
                order_id=order['id'],
                status='filled'
            )
            
            # Добавляем сделку
            self.trades.append(trade)
            self._save_trade_history()
            
            logger.info(f"[REAL] Куплено {amount:.6f} {signal.symbol} по цене {signal.price}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка реальной покупки: {e}")
            return False
    
    def _real_sell_order(self, signal: TradingSignal, amount: float) -> bool:
        """Реальный ордер продажи"""
        try:
            # Размещаем ордер
            order = self.exchange.create_market_sell_order(signal.symbol, amount)
            
            # Создаем сделку
            trade_id = f"real_sell_{order['id']}"
            trade = Trade(
                id=trade_id,
                symbol=signal.symbol,
                side='sell',
                amount=amount,
                price=signal.price,
                timestamp=signal.timestamp,
                exchange=self.default_exchange,
                order_id=order['id'],
                status='filled'
            )
            
            # Добавляем сделку
            self.trades.append(trade)
            self._save_trade_history()
            
            logger.info(f"[REAL] Продано {amount:.6f} {signal.symbol} по цене {signal.price}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка реальной продажи: {e}")
            return False
    
    def update_positions(self):
        """Обновление текущих позиций"""
        try:
            for symbol, position in self.positions.items():
                # Получаем текущую цену
                ticker = self.data_fetcher.get_ticker(symbol)
                current_price = ticker['last']
                
                # Обновляем позицию
                position.current_price = current_price
                if position.side == 'long':
                    position.unrealized_pnl = (current_price - position.entry_price) * position.amount
                else:
                    position.unrealized_pnl = (position.entry_price - current_price) * position.amount
                    
        except Exception as e:
            logger.error(f"Ошибка обновления позиций: {e}")
    
    def get_balance(self) -> Dict[str, float]:
        """Получение текущего баланса"""
        if self.simulation_mode:
            return self.balance.copy()
        else:
            try:
                return self.exchange.fetch_balance()
            except Exception as e:
                logger.error(f"Ошибка получения баланса: {e}")
                return {}
    
    def get_positions(self) -> Dict[str, Position]:
        """Получение текущих позиций"""
        return self.positions.copy()
    
    def get_trades(self, limit: int = 50) -> List[Trade]:
        """Получение истории сделок"""
        return self.trades[-limit:] if limit > 0 else self.trades
    
    def get_trading_stats(self) -> Dict:
        """Получение статистики торговли"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'avg_trade': 0.0
            }
        
        # Статистика по закрытым позициям
        closed_trades = [t for t in self.trades if t.side == 'sell' and t.pnl is not None]
        
        total_trades = len(closed_trades)
        total_pnl = sum(t.pnl for t in closed_trades)
        winning_trades = len([t for t in closed_trades if t.pnl > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_trade = total_pnl / total_trades if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'avg_trade': avg_trade,
            'current_positions': len(self.positions)
        }
    
    def _save_trade_history(self):
        """Сохранение истории сделок"""
        try:
            history_file = 'trade_history.json'
            history_data = []
            
            for trade in self.trades:
                history_data.append({
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'amount': trade.amount,
                    'price': trade.price,
                    'timestamp': trade.timestamp.isoformat(),
                    'exchange': trade.exchange,
                    'order_id': trade.order_id,
                    'status': trade.status,
                    'fee': trade.fee,
                    'pnl': trade.pnl
                })
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения истории сделок: {e}")
    
    def _load_trade_history(self):
        """Загрузка истории сделок"""
        try:
            history_file = 'trade_history.json'
            if not os.path.exists(history_file):
                return
            
            with open(history_file, 'r') as f:
                history_data = json.load(f)
            
            for trade_data in history_data:
                trade = Trade(
                    id=trade_data['id'],
                    symbol=trade_data['symbol'],
                    side=trade_data['side'],
                    amount=trade_data['amount'],
                    price=trade_data['price'],
                    timestamp=datetime.fromisoformat(trade_data['timestamp']),
                    exchange=trade_data['exchange'],
                    order_id=trade_data.get('order_id'),
                    status=trade_data.get('status', 'filled'),
                    fee=trade_data.get('fee', 0.0),
                    pnl=trade_data.get('pnl')
                )
                self.trades.append(trade)
            
            logger.info(f"Загружено {len(self.trades)} сделок из истории")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки истории сделок: {e}")
    
    @staticmethod
    def _str_to_bool(value) -> bool:
        """Преобразование строки в булево значение"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
