"""
Модуль для расчета технических индикаторов
Использует pandas_ta для расчета индикаторов
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class IndicatorConfig:
    """Конфигурация индикатора"""
    name: str
    enabled: bool
    params: Dict


class TechnicalIndicators:
    """Класс для расчета технических индикаторов"""
    
    def __init__(self, config: Dict):
        """
        Инициализация калькулятора индикаторов
        
        Args:
            config: Конфигурация индикаторов из config.yaml
        """
        self.config = config
        self.indicators_config = self._parse_indicators_config()
        
    def _parse_indicators_config(self) -> Dict[str, IndicatorConfig]:
        """Парсинг конфигурации индикаторов"""
        indicators = {}
        strategy_config = self.config.get('strategy', {})
        indicators_config = strategy_config.get('indicators', {})
        
        # EMA настройки
        indicators['ema'] = IndicatorConfig(
            name='ema',
            enabled=True,
            params={
                'fast': strategy_config.get('ema_fast', 9),
                'slow': strategy_config.get('ema_slow', 21)
            }
        )
        
        # ADX
        indicators['adx'] = IndicatorConfig(
            name='adx',
            enabled=indicators_config.get('use_adx', False),
            params={
                'length': indicators_config.get('adx_length', 14),
                'smoothing': indicators_config.get('adx_smoothing', 14),
                'min_threshold': indicators_config.get('adx_min', 20)
            }
        )
        
        # MACD
        indicators['macd'] = IndicatorConfig(
            name='macd',
            enabled=indicators_config.get('use_macd', False),
            params={
                'fast': indicators_config.get('macd_fast', 12),
                'slow': indicators_config.get('macd_slow', 26),
                'signal': indicators_config.get('macd_signal', 9)
            }
        )
        
        # RSI
        indicators['rsi'] = IndicatorConfig(
            name='rsi',
            enabled=indicators_config.get('use_rsi', False),
            params={
                'length': indicators_config.get('rsi_length', 14),
                'overbought': indicators_config.get('rsi_overbought', 70),
                'oversold': indicators_config.get('rsi_oversold', 30)
            }
        )
        
        # TSI
        indicators['tsi'] = IndicatorConfig(
            name='tsi',
            enabled=indicators_config.get('use_tsi', False),
            params={
                'long': indicators_config.get('tsi_long', 25),
                'short': indicators_config.get('tsi_short', 13)
            }
        )
        
        # KDJ
        indicators['kdj'] = IndicatorConfig(
            name='kdj',
            enabled=indicators_config.get('use_kdj', False),
            params={
                'period': indicators_config.get('kdj_period', 9),
                'signal': indicators_config.get('kdj_signal', 3)
            }
        )
        
        # VWAP
        indicators['vwap'] = IndicatorConfig(
            name='vwap',
            enabled=indicators_config.get('use_vwap', False),
            params={
                'period': indicators_config.get('vwap_period', 20)
            }
        )
        
        # ATR
        indicators['atr'] = IndicatorConfig(
            name='atr',
            enabled=indicators_config.get('use_atr', False),
            params={
                'length': indicators_config.get('atr_length', 14),
                'multiplier': indicators_config.get('atr_multiplier', 2.0)
            }
        )
        
        return indicators
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Расчет всех включенных индикаторов
        
        Args:
            df: DataFrame с OHLCV данными
            
        Returns:
            DataFrame с добавленными индикаторами
        """
        result_df = df.copy()
        
        try:
            # EMA (всегда рассчитывается)
            result_df = self._calculate_ema(result_df)
            
            # Остальные индикаторы (если включены)
            for indicator_name, config in self.indicators_config.items():
                if indicator_name == 'ema':
                    continue  # EMA уже рассчитан
                    
                if config.enabled:
                    try:
                        if indicator_name == 'adx':
                            result_df = self._calculate_adx(result_df)
                        elif indicator_name == 'macd':
                            result_df = self._calculate_macd(result_df)
                        elif indicator_name == 'rsi':
                            result_df = self._calculate_rsi(result_df)
                        elif indicator_name == 'tsi':
                            result_df = self._calculate_tsi(result_df)
                        elif indicator_name == 'kdj':
                            result_df = self._calculate_kdj(result_df)
                        elif indicator_name == 'vwap':
                            result_df = self._calculate_vwap(result_df)
                        elif indicator_name == 'atr':
                            result_df = self._calculate_atr(result_df)
                            
                        logger.debug(f"Рассчитан индикатор: {indicator_name}")
                    except Exception as e:
                        logger.error(f"Ошибка расчета индикатора {indicator_name}: {e}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Ошибка расчета индикаторов: {e}")
            return df
    
    def _calculate_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет EMA"""
        config = self.indicators_config['ema']
        fast = config.params['fast']
        slow = config.params['slow']
        
        df[f'EMA_{fast}'] = df['close'].ewm(span=fast).mean()
        df[f'EMA_{slow}'] = df['close'].ewm(span=slow).mean()
        
        return df
    
    def _calculate_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет ADX (упрощенная версия)"""
        config = self.indicators_config['adx']
        length = config.params['length']
        
        # Упрощенный расчет ADX
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=length).mean()
        
        # Простой ADX как отношение волатильности к ATR
        df['ADX'] = (high_low.rolling(window=length).std() / atr) * 100
        df['ADX_POS'] = df['ADX'] * 0.7  # Упрощение
        df['ADX_NEG'] = df['ADX'] * 0.3  # Упрощение
        
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет MACD"""
        config = self.indicators_config['macd']
        fast = config.params['fast']
        slow = config.params['slow']
        signal = config.params['signal']
        
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=signal).mean()
        df['MACD_HIST'] = df['MACD'] - df['MACD_SIGNAL']
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет RSI"""
        config = self.indicators_config['rsi']
        length = config.params['length']
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def _calculate_tsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет TSI (True Strength Index)"""
        config = self.indicators_config['tsi']
        long = config.params['long']
        short = config.params['short']
        
        # TSI = 100 * (EMA(EMA(price_change, short), long) / EMA(EMA(abs(price_change), short), long))
        price_change = df['close'].diff()
        ema1 = price_change.ewm(span=short).mean()
        ema2 = ema1.ewm(span=long).mean()
        ema3 = np.abs(price_change).ewm(span=short).mean()
        ema4 = ema3.ewm(span=long).mean()
        
        df['TSI'] = 100 * (ema2 / ema4)
        
        return df
    
    def _calculate_kdj(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет KDJ"""
        config = self.indicators_config['kdj']
        period = config.params['period']
        signal = config.params['signal']
        
        # KDJ - это модификация стохастика
        lowest_low = df['low'].rolling(window=period).min()
        highest_high = df['high'].rolling(window=period).max()
        
        k = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        df['KDJ_K'] = k.rolling(window=signal).mean()
        df['KDJ_D'] = df['KDJ_K'].rolling(window=signal).mean()
        # J = 3*K - 2*D
        df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
        
        return df
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет VWAP"""
        config = self.indicators_config['vwap']
        period = config.params['period']
        
        # VWAP = Σ(Price * Volume) / Σ(Volume) для заданного периода
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        df['VWAP'] = (typical_price * df['volume']).rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
        
        return df
    
    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет ATR"""
        config = self.indicators_config['atr']
        length = config.params['length']
        multiplier = config.params['multiplier']
        
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df['ATR'] = true_range.rolling(window=length).mean()
        df['ATR_UPPER'] = df['close'] + (df['ATR'] * multiplier)
        df['ATR_LOWER'] = df['close'] - (df['ATR'] * multiplier)
        
        return df
    
    def get_indicator_value(self, df: pd.DataFrame, indicator: str, 
                           index: int = -1) -> Optional[float]:
        """
        Получение значения индикатора на определенном баре
        
        Args:
            df: DataFrame с индикаторами
            indicator: Название индикатора
            index: Индекс бара (-1 для последнего)
            
        Returns:
            Значение индикатора или None
        """
        try:
            if indicator in df.columns:
                return float(df[indicator].iloc[index])
            return None
        except (IndexError, KeyError, ValueError):
            return None
    
    def get_ema_cross_signal(self, df: pd.DataFrame, index: int = -1) -> str:
        """
        Определение сигнала пересечения EMA
        
        Args:
            df: DataFrame с EMA
            index: Индекс бара
            
        Returns:
            'BUY', 'SELL' или 'HOLD'
        """
        try:
            config = self.indicators_config['ema']
            fast_col = f"EMA_{config.params['fast']}"
            slow_col = f"EMA_{config.params['slow']}"
            
            if index == -1:
                current_fast = df[fast_col].iloc[-1]
                current_slow = df[slow_col].iloc[-1]
                prev_fast = df[fast_col].iloc[-2]
                prev_slow = df[slow_col].iloc[-2]
            else:
                current_fast = df[fast_col].iloc[index]
                current_slow = df[slow_col].iloc[index]
                prev_fast = df[fast_col].iloc[index-1]
                prev_slow = df[slow_col].iloc[index-1]
            
            # Быстрая EMA пересекает медленную снизу вверх
            if prev_fast <= prev_slow and current_fast > current_slow:
                return 'BUY'
            # Быстрая EMA пересекает медленную сверху вниз
            elif prev_fast >= prev_slow and current_fast < current_slow:
                return 'SELL'
            else:
                return 'HOLD'
                
        except (IndexError, KeyError, ValueError):
            return 'HOLD'
    
    def get_filter_signals(self, df: pd.DataFrame, index: int = -1) -> Dict[str, bool]:
        """
        Получение сигналов фильтров
        
        Args:
            df: DataFrame с индикаторами
            index: Индекс бара
            
        Returns:
            Словарь с результатами фильтров
        """
        signals = {}
        
        # ADX фильтр
        if self.indicators_config['adx'].enabled:
            adx_value = self.get_indicator_value(df, 'ADX', index)
            min_threshold = self.indicators_config['adx'].params['min_threshold']
            signals['adx'] = adx_value is not None and adx_value > min_threshold
        
        # MACD фильтр
        if self.indicators_config['macd'].enabled:
            macd = self.get_indicator_value(df, 'MACD', index)
            macd_signal = self.get_indicator_value(df, 'MACD_SIGNAL', index)
            signals['macd'] = (macd is not None and macd_signal is not None and 
                             macd > macd_signal)
        
        # RSI фильтр
        if self.indicators_config['rsi'].enabled:
            rsi = self.get_indicator_value(df, 'RSI', index)
            oversold = self.indicators_config['rsi'].params['oversold']
            overbought = self.indicators_config['rsi'].params['overbought']
            signals['rsi'] = (rsi is not None and 
                            oversold < rsi < overbought)
        
        # TSI фильтр
        if self.indicators_config['tsi'].enabled:
            tsi = self.get_indicator_value(df, 'TSI', index)
            signals['tsi'] = tsi is not None and tsi > 0
        
        # KDJ фильтр
        if self.indicators_config['kdj'].enabled:
            kdj_k = self.get_indicator_value(df, 'KDJ_K', index)
            kdj_d = self.get_indicator_value(df, 'KDJ_D', index)
            signals['kdj'] = (kdj_k is not None and kdj_d is not None and 
                            kdj_k > kdj_d)
        
        # VWAP фильтр
        if self.indicators_config['vwap'].enabled:
            close = df['close'].iloc[index]
            vwap = self.get_indicator_value(df, 'VWAP', index)
            signals['vwap'] = (close is not None and vwap is not None and 
                             close > vwap)
        
        # ATR фильтр (проверка волатильности)
        if self.indicators_config['atr'].enabled:
            atr = self.get_indicator_value(df, 'ATR', index)
            close = df['close'].iloc[index]
            # Проверяем, что волатильность не слишком высокая
            signals['atr'] = (atr is not None and close is not None and 
                            atr < close * 0.05)  # ATR меньше 5% от цены
        
        return signals
    
    def get_enabled_indicators(self) -> List[str]:
        """Получение списка включенных индикаторов"""
        return [name for name, config in self.indicators_config.items() 
                if config.enabled]
    
    def update_config(self, new_config: Dict):
        """Обновление конфигурации индикаторов"""
        self.config = new_config
        self.indicators_config = self._parse_indicators_config()
        logger.info("Конфигурация индикаторов обновлена")
