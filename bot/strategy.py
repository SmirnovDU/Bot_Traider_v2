"""
Модуль стратегии торгового бота
Реализует логику принятия торговых решений на основе индикаторов
"""

import pandas as pd
from loguru import logger
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .indicators import TechnicalIndicators


class SignalType(Enum):
    """Типы торговых сигналов"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradingSignal:
    """Торговый сигнал"""
    signal_type: SignalType
    symbol: str
    price: float
    timestamp: datetime
    confidence: float  # Уверенность в сигнале (0-1)
    filters_passed: Dict[str, bool]  # Какие фильтры прошли
    indicators_data: Dict[str, float]  # Данные индикаторов
    reason: str  # Причина сигнала


class TradingStrategy:
    """Основной класс торговой стратегии"""
    
    def __init__(self, config: Dict, indicators: TechnicalIndicators):
        """
        Инициализация стратегии
        
        Args:
            config: Конфигурация из config.yaml
            indicators: Объект для расчета индикаторов
        """
        self.config = config
        self.indicators = indicators
        self.strategy_config = config.get('strategy', {})
        
        # Настройки стратегии
        self.symbol = self.strategy_config.get('symbol', 'BTC/USDT')
        self.timeframe = self.strategy_config.get('timeframe', '15m')
        
        # История сигналов
        self.signal_history: List[TradingSignal] = []
        
        # Состояние позиции
        self.current_position = None  # 'long', 'short', None
        self.entry_price = None
        self.entry_time = None
        
        logger.info(f"Инициализирована стратегия для {self.symbol} {self.timeframe}")
    
    def analyze_market(self, df: pd.DataFrame) -> TradingSignal:
        """
        Анализ рынка и генерация торгового сигнала
        
        Args:
            df: DataFrame с OHLCV данными и индикаторами
            
        Returns:
            TradingSignal объект
        """
        try:
            if len(df) < 50:  # Минимум данных для анализа
                return self._create_hold_signal(df, "Недостаточно данных для анализа")
            
            # Получаем последние данные
            current_price = df['close'].iloc[-1]
            current_time = df.index[-1]
            
            # Основной сигнал от EMA
            ema_signal = self.indicators.get_ema_cross_signal(df)
            
            # Получаем сигналы фильтров
            filter_signals = self.indicators.get_filter_signals(df)
            
            # Анализируем сигнал
            if ema_signal == 'BUY':
                return self._analyze_buy_signal(df, current_price, current_time, filter_signals)
            elif ema_signal == 'SELL':
                return self._analyze_sell_signal(df, current_price, current_time, filter_signals)
            else:
                return self._create_hold_signal(df, "Нет пересечения EMA")
                
        except Exception as e:
            logger.error(f"Ошибка анализа рынка: {e}")
            return self._create_hold_signal(df, f"Ошибка анализа: {e}")
    
    def _analyze_buy_signal(self, df: pd.DataFrame, price: float, 
                           timestamp: datetime, filters: Dict[str, bool]) -> TradingSignal:
        """Анализ сигнала на покупку"""
        try:
            # Проверяем, что у нас нет открытой позиции
            if self.current_position == 'long':
                return self._create_hold_signal(df, "Уже есть длинная позиция")
            
            # Подсчитываем пройденные фильтры
            enabled_filters = [name for name, config in self.indicators.indicators_config.items() 
                             if config.enabled and name != 'ema']
            
            passed_filters = 0
            total_filters = len(enabled_filters)
            
            for filter_name in enabled_filters:
                if filters.get(filter_name, False):
                    passed_filters += 1
            
            # Рассчитываем уверенность
            if total_filters == 0:
                confidence = 0.8  # Если нет фильтров, базовая уверенность
            else:
                confidence = 0.5 + (passed_filters / total_filters) * 0.4
            
            # Минимальная уверенность для входа
            min_confidence = 0.6
            
            if confidence >= min_confidence:
                # Получаем данные индикаторов
                indicators_data = self._get_indicators_data(df)
                
                signal = TradingSignal(
                    signal_type=SignalType.BUY,
                    symbol=self.symbol,
                    price=price,
                    timestamp=timestamp,
                    confidence=confidence,
                    filters_passed=filters,
                    indicators_data=indicators_data,
                    reason=f"EMA пересечение вверх, пройдено {passed_filters}/{total_filters} фильтров"
                )
                
                logger.info(f"Сгенерирован сигнал BUY: {signal.reason}, уверенность: {confidence:.2f}")
                return signal
            else:
                return self._create_hold_signal(df, 
                    f"Недостаточная уверенность: {confidence:.2f} < {min_confidence}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа сигнала покупки: {e}")
            return self._create_hold_signal(df, f"Ошибка анализа покупки: {e}")
    
    def _analyze_sell_signal(self, df: pd.DataFrame, price: float, 
                            timestamp: datetime, filters: Dict[str, bool]) -> TradingSignal:
        """Анализ сигнала на продажу"""
        try:
            # Проверяем, что у нас есть длинная позиция
            if self.current_position != 'long':
                return self._create_hold_signal(df, "Нет длинной позиции для закрытия")
            
            # Для продажи фильтры менее критичны
            enabled_filters = [name for name, config in self.indicators.indicators_config.items() 
                             if config.enabled and name != 'ema']
            
            passed_filters = 0
            total_filters = len(enabled_filters)
            
            for filter_name in enabled_filters:
                if filters.get(filter_name, False):
                    passed_filters += 1
            
            # Рассчитываем уверенность (для продажи требования ниже)
            if total_filters == 0:
                confidence = 0.7
            else:
                confidence = 0.4 + (passed_filters / total_filters) * 0.4
            
            # Минимальная уверенность для выхода
            min_confidence = 0.4
            
            if confidence >= min_confidence:
                # Получаем данные индикаторов
                indicators_data = self._get_indicators_data(df)
                
                signal = TradingSignal(
                    signal_type=SignalType.SELL,
                    symbol=self.symbol,
                    price=price,
                    timestamp=timestamp,
                    confidence=confidence,
                    filters_passed=filters,
                    indicators_data=indicators_data,
                    reason=f"EMA пересечение вниз, пройдено {passed_filters}/{total_filters} фильтров"
                )
                
                logger.info(f"Сгенерирован сигнал SELL: {signal.reason}, уверенность: {confidence:.2f}")
                return signal
            else:
                return self._create_hold_signal(df, 
                    f"Недостаточная уверенность для продажи: {confidence:.2f} < {min_confidence}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа сигнала продажи: {e}")
            return self._create_hold_signal(df, f"Ошибка анализа продажи: {e}")
    
    def _create_hold_signal(self, df: pd.DataFrame, reason: str) -> TradingSignal:
        """Создание сигнала HOLD"""
        current_price = df['close'].iloc[-1]
        current_time = df.index[-1]
        indicators_data = self._get_indicators_data(df)
        
        return TradingSignal(
            signal_type=SignalType.HOLD,
            symbol=self.symbol,
            price=current_price,
            timestamp=current_time,
            confidence=0.0,
            filters_passed={},
            indicators_data=indicators_data,
            reason=reason
        )
    
    def _get_indicators_data(self, df: pd.DataFrame) -> Dict[str, float]:
        """Получение данных всех индикаторов"""
        data = {}
        
        # EMA данные
        ema_config = self.indicators.indicators_config['ema']
        fast_col = f"EMA_{ema_config.params['fast']}"
        slow_col = f"EMA_{ema_config.params['slow']}"
        
        if fast_col in df.columns:
            data['ema_fast'] = float(df[fast_col].iloc[-1])
        if slow_col in df.columns:
            data['ema_slow'] = float(df[slow_col].iloc[-1])
        
        # Данные других индикаторов
        indicator_columns = ['ADX', 'MACD', 'MACD_SIGNAL', 'RSI', 'TSI', 
                           'KDJ_K', 'KDJ_D', 'KDJ_J', 'VWAP', 'ATR']
        
        for col in indicator_columns:
            if col in df.columns:
                try:
                    data[col.lower()] = float(df[col].iloc[-1])
                except (ValueError, IndexError):
                    pass
        
        return data
    
    def execute_signal(self, signal: TradingSignal) -> bool:
        """
        Исполнение торгового сигнала
        
        Args:
            signal: Торговый сигнал
            
        Returns:
            True если сигнал исполнен успешно
        """
        try:
            if signal.signal_type == SignalType.BUY:
                return self._execute_buy(signal)
            elif signal.signal_type == SignalType.SELL:
                return self._execute_sell(signal)
            else:
                return True  # HOLD не требует действий
                
        except Exception as e:
            logger.error(f"Ошибка исполнения сигнала: {e}")
            return False
    
    def _execute_buy(self, signal: TradingSignal) -> bool:
        """Исполнение сигнала покупки"""
        try:
            if self.current_position == 'long':
                logger.warning("Попытка купить при уже открытой длинной позиции")
                return False
            
            # Обновляем состояние позиции
            self.current_position = 'long'
            self.entry_price = signal.price
            self.entry_time = signal.timestamp
            
            # Добавляем в историю
            self.signal_history.append(signal)
            
            logger.info(f"Открыта длинная позиция: {signal.symbol} по цене {signal.price}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исполнения покупки: {e}")
            return False
    
    def _execute_sell(self, signal: TradingSignal) -> bool:
        """Исполнение сигнала продажи"""
        try:
            if self.current_position != 'long':
                logger.warning("Попытка продать без открытой длинной позиции")
                return False
            
            # Рассчитываем прибыль/убыток
            if self.entry_price:
                pnl = signal.price - self.entry_price
                pnl_percent = (pnl / self.entry_price) * 100
                logger.info(f"Закрыта длинная позиция: PnL = {pnl:.4f} ({pnl_percent:.2f}%)")
            
            # Обновляем состояние позиции
            self.current_position = None
            self.entry_price = None
            self.entry_time = None
            
            # Добавляем в историю
            self.signal_history.append(signal)
            
            logger.info(f"Закрыта длинная позиция: {signal.symbol} по цене {signal.price}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исполнения продажи: {e}")
            return False
    
    def get_position_info(self) -> Dict:
        """Получение информации о текущей позиции"""
        return {
            'position': self.current_position,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time,
            'symbol': self.symbol
        }
    
    def get_signal_history(self, limit: int = 10) -> List[TradingSignal]:
        """Получение истории сигналов"""
        return self.signal_history[-limit:] if limit > 0 else self.signal_history
    
    def get_strategy_stats(self) -> Dict:
        """Получение статистики стратегии"""
        if not self.signal_history:
            return {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'avg_confidence': 0.0
            }
        
        buy_signals = [s for s in self.signal_history if s.signal_type == SignalType.BUY]
        sell_signals = [s for s in self.signal_history if s.signal_type == SignalType.SELL]
        
        avg_confidence = sum(s.confidence for s in self.signal_history) / len(self.signal_history)
        
        return {
            'total_signals': len(self.signal_history),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'avg_confidence': avg_confidence,
            'current_position': self.current_position
        }
    
    def update_config(self, new_config: Dict):
        """Обновление конфигурации стратегии"""
        self.config = new_config
        self.strategy_config = new_config.get('strategy', {})
        self.symbol = self.strategy_config.get('symbol', 'BTC/USDT')
        self.timeframe = self.strategy_config.get('timeframe', '15m')
        logger.info("Конфигурация стратегии обновлена")
