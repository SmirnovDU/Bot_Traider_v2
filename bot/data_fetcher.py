"""
Модуль для получения рыночных данных с бирж через ccxt
Поддерживает Binance и Bybit
"""

import ccxt
import pandas as pd
from loguru import logger
from typing import Dict, List
import time
from datetime import datetime


class DataFetcher:
    """Класс для получения рыночных данных с бирж"""
    
    def __init__(self, exchange_name: str, api_key: str = "", secret: str = "", 
                 testnet: bool = False, sandbox: bool = False):
        """
        Инициализация DataFetcher
        
        Args:
            exchange_name: Название биржи (binance, bybit)
            api_key: API ключ
            secret: Секретный ключ
            testnet: Использовать тестовую сеть
            sandbox: Использовать песочницу
        """
        self.exchange_name = exchange_name.lower()
        self.api_key = api_key
        self.secret = secret
        self.testnet = testnet
        self.sandbox = sandbox
        
        # Инициализация биржи
        self.exchange = self._init_exchange()
        
        # Кэш для данных
        self._cache = {}
        self._cache_timeout = 60  # секунд
        
    def _init_exchange(self) -> ccxt.Exchange:
        """Инициализация объекта биржи"""
        try:
            if self.exchange_name == "binance":
                exchange_class = ccxt.binance
            elif self.exchange_name == "bybit":
                exchange_class = ccxt.bybit
            else:
                raise ValueError(f"Неподдерживаемая биржа: {self.exchange_name}")
            
            # Настройки для биржи
            config = {
                'apiKey': self.api_key,
                'secret': self.secret,
                'timeout': 30000,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # Spot trading
                }
            }
            
            # Настройки для тестовой сети
            if DataFetcher._str_to_bool(self.testnet):
                if self.exchange_name == "binance":
                    config['sandbox'] = True
                    config['urls'] = {
                        'api': {
                            'public': 'https://testnet.binance.vision/api',
                            'private': 'https://testnet.binance.vision/api',
                        }
                    }
                elif self.exchange_name == "bybit":
                    config['urls'] = {
                        'api': {
                            'public': 'https://api-testnet.bybit.com',
                            'private': 'https://api-testnet.bybit.com',
                        }
                    }
            
            exchange = exchange_class(config)
            
            # Проверка подключения
            if self.api_key and self.secret:
                try:
                    exchange.fetch_balance()
                    logger.info(f"Успешное подключение к {self.exchange_name}")
                except Exception as e:
                    logger.warning(f"Не удалось получить баланс с {self.exchange_name}: {e}")
            else:
                logger.info(f"Подключение к {self.exchange_name} в режиме только чтения")
            
            return exchange
            
        except Exception as e:
            logger.error(f"Ошибка инициализации биржи {self.exchange_name}: {e}")
            raise
    
    @staticmethod
    def _str_to_bool(value) -> bool:
        """Преобразование строки в булево значение"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def get_ohlcv(self, symbol: str, timeframe: str = '15m', 
                  limit: int = 100) -> pd.DataFrame:
        """
        Получение OHLCV данных
        
        Args:
            symbol: Торговая пара (например, 'BTC/USDT')
            timeframe: Таймфрейм ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
            limit: Количество свечей
            
        Returns:
            DataFrame с колонками: timestamp, open, high, low, close, volume
        """
        cache_key = f"{symbol}_{timeframe}_{limit}"
        current_time = time.time()
        
        # Проверяем кэш
        if cache_key in self._cache:
            cached_data, cache_time = self._cache[cache_key]
            if current_time - cache_time < self._cache_timeout:
                logger.debug(f"Используем кэшированные данные для {symbol}")
                return cached_data.copy()
        
        try:
            logger.info(f"Получение данных {symbol} {timeframe} с {self.exchange_name}")
            
            # Получаем данные
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Преобразуем в DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Кэшируем данные
            self._cache[cache_key] = (df.copy(), current_time)
            
            logger.info(f"Получено {len(df)} свечей для {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Ошибка получения данных {symbol}: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Получение текущей цены
        
        Args:
            symbol: Торговая пара
            
        Returns:
            Словарь с информацией о тикере
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Ошибка получения тикера {symbol}: {e}")
            raise
    
    def get_balance(self, currency: str = None) -> Dict:
        """
        Получение баланса
        
        Args:
            currency: Валюта (если None, возвращает все балансы)
            
        Returns:
            Словарь с балансами
        """
        if not self.api_key or not self.secret:
            logger.warning("API ключи не настроены, невозможно получить баланс")
            return {}
        
        try:
            balance = self.exchange.fetch_balance()
            
            if currency:
                return {
                    'free': balance.get(currency, {}).get('free', 0),
                    'used': balance.get(currency, {}).get('used', 0),
                    'total': balance.get(currency, {}).get('total', 0)
                }
            else:
                return balance
                
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return {}
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Получение стакана заявок
        
        Args:
            symbol: Торговая пара
            limit: Количество уровней
            
        Returns:
            Словарь с данными стакана
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': orderbook['bids'],
                'asks': orderbook['asks'],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            logger.error(f"Ошибка получения стакана {symbol}: {e}")
            raise
    
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """
        Получение последних сделок
        
        Args:
            symbol: Торговая пара
            limit: Количество сделок
            
        Returns:
            Список последних сделок
        """
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"Ошибка получения сделок {symbol}: {e}")
            raise
    
    def is_market_open(self, symbol: str) -> bool:
        """
        Проверка, открыт ли рынок
        
        Args:
            symbol: Торговая пара
            
        Returns:
            True если рынок открыт
        """
        try:
            markets = self.exchange.load_markets()
            market = markets.get(symbol)
            if market:
                return market.get('active', True)
            return True
        except Exception as e:
            logger.error(f"Ошибка проверки статуса рынка {symbol}: {e}")
            return True
    
    def get_market_info(self, symbol: str) -> Dict:
        """
        Получение информации о рынке
        
        Args:
            symbol: Торговая пара
            
        Returns:
            Словарь с информацией о рынке
        """
        try:
            markets = self.exchange.load_markets()
            market = markets.get(symbol)
            
            if not market:
                raise ValueError(f"Рынок {symbol} не найден")
            
            return {
                'symbol': symbol,
                'base': market['base'],
                'quote': market['quote'],
                'active': market.get('active', True),
                'precision': market.get('precision', {}),
                'limits': market.get('limits', {}),
                'fees': market.get('fees', {})
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о рынке {symbol}: {e}")
            raise
    
    def clear_cache(self):
        """Очистка кэша"""
        self._cache.clear()
        logger.debug("Кэш данных очищен")


class DataManager:
    """Менеджер для работы с несколькими источниками данных"""
    
    def __init__(self, config: Dict):
        """
        Инициализация менеджера данных
        
        Args:
            config: Конфигурация из config.yaml
        """
        self.config = config
        self.fetchers = {}
        self.default_exchange = config.get('trading', {}).get('default_exchange', 'binance')
        
        # Инициализируем биржи
        self._init_exchanges()
    
    def _init_exchanges(self):
        """Инициализация бирж из конфигурации"""
        exchanges_config = self.config.get('exchanges', {})
        
        for exchange_name, exchange_config in exchanges_config.items():
            if exchange_config.get('enabled', False):
                try:
                    fetcher = DataFetcher(
                        exchange_name=exchange_name,
                        api_key=exchange_config.get('api_key', ''),
                        secret=exchange_config.get('secret_key', ''),
                        testnet=exchange_config.get('testnet', False)
                    )
                    self.fetchers[exchange_name] = fetcher
                    logger.info(f"Инициализирована биржа: {exchange_name}")
                except Exception as e:
                    logger.error(f"Ошибка инициализации биржи {exchange_name}: {e}")
    
    def get_data(self, symbol: str, timeframe: str = '15m', 
                 limit: int = 100, exchange: str = None) -> pd.DataFrame:
        """
        Получение данных с указанной или дефолтной биржи
        
        Args:
            symbol: Торговая пара
            timeframe: Таймфрейм
            limit: Количество свечей
            exchange: Название биржи (если None, используется дефолтная)
            
        Returns:
            DataFrame с OHLCV данными
        """
        if exchange is None:
            exchange = self.default_exchange
        
        if exchange not in self.fetchers:
            raise ValueError(f"Биржа {exchange} не инициализирована")
        
        return self.fetchers[exchange].get_ohlcv(symbol, timeframe, limit)
    
    def get_ticker(self, symbol: str, exchange: str = None) -> Dict:
        """Получение тикера"""
        if exchange is None:
            exchange = self.default_exchange
        
        if exchange not in self.fetchers:
            raise ValueError(f"Биржа {exchange} не инициализирована")
        
        return self.fetchers[exchange].get_ticker(symbol)
    
    def get_balance(self, currency: str = None, exchange: str = None) -> Dict:
        """Получение баланса"""
        if exchange is None:
            exchange = self.default_exchange
        
        if exchange not in self.fetchers:
            raise ValueError(f"Биржа {exchange} не инициализирована")
        
        return self.fetchers[exchange].get_balance(currency)
    
    def get_available_exchanges(self) -> List[str]:
        """Получение списка доступных бирж"""
        return list(self.fetchers.keys())
    
    def clear_all_cache(self):
        """Очистка кэша всех бирж"""
        for fetcher in self.fetchers.values():
            fetcher.clear_cache()
