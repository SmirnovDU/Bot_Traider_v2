import sqlite3
from loguru import logger
from bot.config import DB_PATH, TEST_MODE, TEST_BALANCE_USDT


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT UNIQUE,
        timestamp TEXT,
        exchange TEXT,
        side TEXT,
        symbol TEXT,
        price REAL,
        qty REAL,
        amount_usdt REAL,
        fee REAL,
        profit REAL,
        balance_after REAL,
        note TEXT)
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS balances (
        exchange TEXT,
        coin TEXT,
        amount REAL,
        PRIMARY KEY (exchange, coin)
    )
    """)

    conn.commit()
    conn.close()
    logger.info("База данных инициализирована.")


def init_test_balances():
    """Инициализация тестовых балансов"""
    if TEST_MODE:
        # Единый баланс для обеих бирж в тестовом режиме
        update_balance("Bybit", "USDT", TEST_BALANCE_USDT)
        update_balance("Binance", "USDT", TEST_BALANCE_USDT)
        logger.info(f"Тестовые балансы инициализированы: {TEST_BALANCE_USDT} USDT для обеих бирж")


def get_last_buy_price(exchange, symbol):
    """Получить цену последней покупки для расчёта прибыли"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT price FROM trades 
    WHERE exchange=? AND symbol=? AND side='buy' 
    ORDER BY timestamp DESC LIMIT 1
    """, (exchange, symbol))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def save_trade(data: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO trades (request_id,
                            timestamp,
                            exchange,
                            side,
                            symbol,
                            price,
                            qty,
                            amount_usdt,
                            fee,
                            profit,
                            balance_after,
                            note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data.get("balance_after"),
            data.get("note")
        ))
        conn.commit()
        conn.close()
        logger.info(f"Сделка сохранена: {data.get('request_id')}")
    except Exception as e:
        logger.error(f"Ошибка сохранения сделки: {e}")
        logger.error(f"Данные: {data}")
        raise


def update_balance(exchange, coin, amount):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO balances (exchange, coin, amount)
    VALUES (?, ?, ?)
    ON CONFLICT(exchange, coin) DO UPDATE SET amount=excluded.amount
    """, (exchange, coin, amount))
    conn.commit()
    conn.close()


def get_balance(exchange, coin):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT amount FROM balances WHERE exchange=? AND coin=?", (exchange, coin))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0.0


def get_all_balances():
    """Получить все балансы"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT exchange, coin, amount FROM balances WHERE amount > 0 ORDER BY exchange, coin")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_profit_statistics():
    """Получить статистику по прибыли"""
    conn = sqlite3.connect(DB_PATH)
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
    
    # Общая сумма комиссий
    cur.execute("SELECT SUM(fee) FROM trades")
    total_fees = cur.fetchone()[0] or 0.0
    
    # Общий объём торгов
    cur.execute("SELECT SUM(amount_usdt) FROM trades")
    total_volume = cur.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "total_profit": total_profit,
        "profitable_trades": profitable_trades,
        "losing_trades": losing_trades,
        "total_trades_with_profit": total_trades_with_profit,
        "avg_profit": avg_profit,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "total_fees": total_fees,
        "total_volume": total_volume,
        "win_rate": (profitable_trades / total_trades_with_profit * 100) if total_trades_with_profit > 0 else 0
    }


def get_trades_summary():
    """Получить краткую сводку по сделкам"""
    conn = sqlite3.connect(DB_PATH)
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
    
    return {
        "total_trades": total_trades,
        "recent_trades": recent_trades
    }
