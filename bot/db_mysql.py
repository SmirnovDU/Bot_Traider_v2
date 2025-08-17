import mysql.connector
from loguru import logger
from bot.config import TEST_MODE, TEST_BALANCE_USDT, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def get_connection():
    """Получить соединение с MySQL"""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            autocommit=True
        )
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Ошибка подключения к MySQL: {e}")
        raise

def init_db():
    """Инициализация базы данных MySQL"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Создаём таблицу сделок
        cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id VARCHAR(255) UNIQUE NOT NULL,
            timestamp DATETIME NOT NULL,
            exchange VARCHAR(50),
            side VARCHAR(10),
            symbol VARCHAR(50),
            price DECIMAL(20,8),
            qty DECIMAL(20,8),
            amount_usdt DECIMAL(20,8),
            fee DECIMAL(20,8),
            profit DECIMAL(20,8),
            profit_no_fees DECIMAL(20,8),
            balance_after DECIMAL(20,8),
            note TEXT,
            INDEX idx_exchange_symbol (exchange, symbol),
            INDEX idx_side (side),
            INDEX idx_timestamp (timestamp)
        )
        """)
        
        # Создаём таблицу балансов
        cur.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            exchange VARCHAR(50),
            coin VARCHAR(20),
            amount DECIMAL(20,8),
            PRIMARY KEY (exchange, coin)
        )
        """)
        
        conn.close()
        logger.info("База данных MySQL инициализирована.")
        
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        raise

def init_test_balances():
    """Инициализация тестовых балансов только если их еще нет"""
    if TEST_MODE:
        # Проверяем, есть ли уже балансы
        bybit_balance = get_balance("Bybit", "USDT")
        binance_balance = get_balance("Binance", "USDT")
        
        # Инициализируем только если балансов нет (первый запуск)
        if bybit_balance == 0.0:
            update_balance("Bybit", "USDT", TEST_BALANCE_USDT)
            logger.info(f"Инициализирован тестовый баланс Bybit: {TEST_BALANCE_USDT} USDT")
        else:
            logger.info(f"Существующий баланс Bybit: {bybit_balance} USDT")
            
        if binance_balance == 0.0:
            update_balance("Binance", "USDT", TEST_BALANCE_USDT)
            logger.info(f"Инициализирован тестовый баланс Binance: {TEST_BALANCE_USDT} USDT")
        else:
            logger.info(f"Существующий баланс Binance: {binance_balance} USDT")

def get_last_buy_price(exchange, symbol):
    """Получить цену последней покупки для расчёта прибыли"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT price FROM trades 
        WHERE exchange=%s AND symbol=%s AND side='buy' 
        ORDER BY timestamp DESC LIMIT 1
        """, (exchange, symbol))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Ошибка получения последней цены покупки: {e}")
        return None

def has_previous_buy(exchange, symbol):
    """Проверить, была ли покупка этой монеты ранее"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT COUNT(*) FROM trades 
        WHERE exchange=%s AND symbol=%s AND side='buy'
        """, (exchange, symbol))
        count = cur.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки предыдущих покупок: {e}")
        return False

def get_unsold_quantity(exchange, symbol):
    """Получить количество непроданной монеты (покупки минус продажи)"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Суммируем покупки
        cur.execute("""
        SELECT COALESCE(SUM(qty), 0) FROM trades 
        WHERE exchange=%s AND symbol=%s AND side='buy'
        """, (exchange, symbol))
        total_bought = cur.fetchone()[0] or 0
        
        # Суммируем продажи
        cur.execute("""
        SELECT COALESCE(SUM(qty), 0) FROM trades 
        WHERE exchange=%s AND symbol=%s AND side='sell'
        """, (exchange, symbol))
        total_sold = cur.fetchone()[0] or 0
        
        conn.close()
        return max(0, float(total_bought - total_sold))
    except Exception as e:
        logger.error(f"Ошибка получения непроданного количества: {e}")
        return 0.0

def get_exchange_with_coins(symbol):
    """Найти биржу с максимальным количеством непроданных монет"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Получаем балансы монет по биржам (покупки - продажи)
        cur.execute("""
        SELECT exchange, 
               COALESCE(SUM(CASE WHEN side='buy' THEN qty ELSE 0 END), 0) - 
               COALESCE(SUM(CASE WHEN side='sell' THEN qty ELSE 0 END), 0) as balance
        FROM trades 
        WHERE symbol=%s 
        GROUP BY exchange
        HAVING balance > 0
        ORDER BY balance DESC
        LIMIT 1
        """, (symbol,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return result[0]  # Возвращаем название биржи
        else:
            return None
    except Exception as e:
        logger.error(f"Ошибка поиска биржи с монетами: {e}")
        return None

def save_trade(data: dict):
    """Сохранить сделку в БД"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO trades (request_id, timestamp, exchange, side, symbol, 
                           price, qty, amount_usdt, fee, profit, profit_no_fees, balance_after, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("request_id"),
            data.get("timestamp"),
            data.get("exchange"),
            data.get("side"),
            data.get("symbol"),
            data.get("price"),
            data.get("qty"),
            data.get("amount_usdt"),
            data.get("fee"),
            data.get("profit"),
            data.get("profit_no_fees"),
            data.get("balance_after"),
            data.get("note")
        ))
        conn.commit()  # Критически важно!
        conn.close()
        logger.info(f"Сделка сохранена: {data.get('request_id')}")
    except mysql.connector.IntegrityError:
        logger.warning(f"Сделка уже существует: {data.get('request_id')}")
    except Exception as e:
        logger.error(f"Ошибка сохранения сделки: {e}")
        logger.error(f"Данные: {data}")

def get_balance(exchange, coin):
    """Получить баланс монеты на бирже"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT amount FROM balances WHERE exchange=%s AND coin=%s", 
                   (exchange, coin))
        row = cur.fetchone()
        conn.close()
        return float(row[0]) if row else 0.0
    except Exception as e:
        logger.error(f"Ошибка получения баланса: {e}")
        return 0.0

def update_balance(exchange, coin, amount):
    """Обновить баланс монеты на бирже"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO balances (exchange, coin, amount) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE amount=%s
        """, (exchange, coin, amount, amount))
        conn.commit()  # Критически важно!
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка обновления баланса: {e}")

def get_all_balances():
    """Получить все балансы"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT exchange, coin, amount FROM balances WHERE amount > 0 ORDER BY exchange, coin")
        rows = cur.fetchall()
        conn.close()
        
        # Преобразуем в список словарей для удобства
        return [
            {
                "exchange": row[0],
                "coin": row[1], 
                "amount": float(row[2])
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Ошибка получения балансов: {e}")
        return []

def get_profit_statistics():
    """Получить статистику по прибыли"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Общая прибыль
        cur.execute("SELECT SUM(profit) FROM trades WHERE profit IS NOT NULL")
        total_profit = cur.fetchone()[0] or 0.0
        
        # Количество прибыльных сделок
        cur.execute("SELECT COUNT(*) FROM trades WHERE profit > 0")
        profitable_trades = cur.fetchone()[0] or 0
        
        # Количество убыточных сделок
        cur.execute("SELECT COUNT(*) FROM trades WHERE profit < 0")
        losing_trades = cur.fetchone()[0] or 0
        
        # Общее количество сделок с прибылью (продажи)
        cur.execute("SELECT COUNT(*) FROM trades WHERE profit IS NOT NULL")
        total_trades_with_profit = cur.fetchone()[0] or 0
        
        # Средняя прибыль на сделку
        cur.execute("SELECT AVG(profit) FROM trades WHERE profit IS NOT NULL")
        avg_profit = cur.fetchone()[0] or 0.0
        
        # Лучшая сделка
        cur.execute("SELECT MAX(profit) FROM trades WHERE profit IS NOT NULL")
        best_trade = cur.fetchone()[0] or 0.0
        
        # Худшая сделка
        cur.execute("SELECT MIN(profit) FROM trades WHERE profit IS NOT NULL")
        worst_trade = cur.fetchone()[0] or 0.0
        
        # Общие комиссии
        cur.execute("SELECT SUM(fee) FROM trades WHERE fee IS NOT NULL")
        total_fees = cur.fetchone()[0] or 0.0
        
        # Общий объём торгов
        cur.execute("SELECT SUM(amount_usdt) FROM trades WHERE amount_usdt IS NOT NULL")
        total_volume = cur.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_profit": float(total_profit),
            "profitable_trades": profitable_trades,
            "losing_trades": losing_trades,
            "total_trades_with_profit": total_trades_with_profit,
            "avg_profit": float(avg_profit),
            "best_trade": float(best_trade),
            "worst_trade": float(worst_trade),
            "total_fees": float(total_fees),
            "total_volume": float(total_volume),
            "win_rate": (profitable_trades / total_trades_with_profit * 100) if total_trades_with_profit > 0 else 0
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики прибыли: {e}")
        return {
            "total_profit": 0.0, "profitable_trades": 0, "losing_trades": 0,
            "total_trades_with_profit": 0, "avg_profit": 0.0, "best_trade": 0.0,
            "worst_trade": 0.0, "total_fees": 0.0, "total_volume": 0.0, "win_rate": 0.0
        }


def get_profit_statistics_no_fees():
    """Получить статистику по прибыли БЕЗ комиссий (анализ стратегии)"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Общая прибыль БЕЗ комиссий
        cur.execute("SELECT SUM(profit_no_fees) FROM trades WHERE profit_no_fees IS NOT NULL")
        total_profit_no_fees = cur.fetchone()[0] or 0.0
        
        # Количество прибыльных сделок БЕЗ комиссий
        cur.execute("SELECT COUNT(*) FROM trades WHERE profit_no_fees > 0")
        profitable_trades_no_fees = cur.fetchone()[0] or 0
        
        # Количество убыточных сделок БЕЗ комиссий
        cur.execute("SELECT COUNT(*) FROM trades WHERE profit_no_fees < 0")
        losing_trades_no_fees = cur.fetchone()[0] or 0
        
        # Общее количество сделок с прибылью БЕЗ комиссий
        cur.execute("SELECT COUNT(*) FROM trades WHERE profit_no_fees IS NOT NULL")
        total_trades_with_profit_no_fees = cur.fetchone()[0] or 0
        
        # Средняя прибыль БЕЗ комиссий
        cur.execute("SELECT AVG(profit_no_fees) FROM trades WHERE profit_no_fees IS NOT NULL")
        avg_profit_no_fees = cur.fetchone()[0] or 0.0
        
        # Лучшая сделка БЕЗ комиссий
        cur.execute("SELECT MAX(profit_no_fees) FROM trades WHERE profit_no_fees IS NOT NULL")
        best_trade_no_fees = cur.fetchone()[0] or 0.0
        
        # Худшая сделка БЕЗ комиссий
        cur.execute("SELECT MIN(profit_no_fees) FROM trades WHERE profit_no_fees IS NOT NULL")
        worst_trade_no_fees = cur.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_profit_no_fees": float(total_profit_no_fees),
            "profitable_trades_no_fees": profitable_trades_no_fees,
            "losing_trades_no_fees": losing_trades_no_fees,
            "total_trades_with_profit_no_fees": total_trades_with_profit_no_fees,
            "avg_profit_no_fees": float(avg_profit_no_fees),
            "best_trade_no_fees": float(best_trade_no_fees),
            "worst_trade_no_fees": float(worst_trade_no_fees),
            "win_rate_no_fees": (profitable_trades_no_fees / total_trades_with_profit_no_fees * 100) if total_trades_with_profit_no_fees > 0 else 0
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики прибыли: {e}")
        return {
            "total_profit": 0.0, "profitable_trades": 0, "losing_trades": 0,
            "total_trades_with_profit": 0, "avg_profit": 0.0, "best_trade": 0.0,
            "worst_trade": 0.0, "total_fees": 0.0, "total_volume": 0.0, "win_rate": 0.0
        }

def get_trades_summary():
    """Получить краткую сводку по сделкам"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Последние 5 сделок
        cur.execute("""
        SELECT timestamp, exchange, side, symbol, price, qty, amount_usdt, profit 
        FROM trades 
        ORDER BY timestamp DESC 
        LIMIT 5
        """)
        recent_trades = cur.fetchall()
        
        # Общее количество сделок
        cur.execute("SELECT COUNT(*) FROM trades")
        total_trades = cur.fetchone()[0] or 0
        
        conn.close()
        
        # Преобразуем recent_trades в список словарей
        recent_trades_dict = [
            {
                "timestamp": row[0].isoformat() if row[0] else "",
                "exchange": row[1],
                "side": row[2],
                "symbol": row[3],
                "price": float(row[4]) if row[4] else 0.0,
                "qty": float(row[5]) if row[5] else 0.0,
                "amount_usdt": float(row[6]) if row[6] else 0.0,
                "profit": float(row[7]) if row[7] else None
            }
            for row in recent_trades
        ]
        
        return {
            "total_trades": total_trades,
            "recent_trades": recent_trades_dict
        }
    except Exception as e:
        logger.error(f"Ошибка получения сводки сделок: {e}")
        return {"total_trades": 0, "recent_trades": []}
