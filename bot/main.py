from fastapi import FastAPI
from loguru import logger
from bot.db import init_db, init_test_balances
from bot.webhook import router as webhook_router
from bot.exchanges.bybit import BybitExchange
from bot.exchanges.binance import BinanceExchange
from bot.config import TEST_MODE

app = FastAPI()

# Инициализируем экземпляры бирж
bybit = BybitExchange()
binance = BinanceExchange()


@app.on_event("startup")
def startup():
    logger.add("bot.log", rotation="10 MB",
               retention="7 days", compression="zip")
    init_db()
    
    if TEST_MODE:
        init_test_balances()
        logger.info("Тестовый режим активирован")
    else:
        # Инициализируем реальные балансы
        bybit.init_balances()
        binance.init_balances()
        logger.info("Боевой режим активирован")
    
    logger.info("Бот запущен.")


app.include_router(webhook_router)


@app.get("/status")
def root():
    return {"status": "ok"}


@app.get("/balances")
def get_balances():
    """Получить текущие балансы"""
    from bot.db import get_all_balances
    balances = get_all_balances()
    return {"balances": balances}
