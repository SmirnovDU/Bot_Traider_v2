from fastapi import FastAPI
from loguru import logger
from bot.db import init_db, init_test_balances
from bot.webhook import router as webhook_router
from bot.exchanges.bybit import BybitExchange
from bot.exchanges.binance import BinanceExchange
from bot.config import TEST_MODE
from bot.telegram_notifier import notify_status
import uvicorn
import os
import asyncio

app = FastAPI()

# Инициализируем экземпляры бирж
bybit = BybitExchange()
binance = BinanceExchange()


@app.on_event("startup")
async def startup():
    logger.add("bot.log", rotation="10 MB",
               retention="7 days", compression="zip")
    init_db()
    
    if TEST_MODE:
        init_test_balances()
        logger.info("Тестовый режим активирован")
        mode = "Тестовый режим"
    else:
        # Инициализируем реальные балансы
        bybit.init_balances()
        binance.init_balances()
        logger.info("Боевой режим активирован")
        mode = "Боевой режим"
    
    logger.info("Бот запущен.")
    
    # Отправляем уведомление о запуске в Telegram
    try:
        await notify_status("Бот запущен и готов к работе", {
            "Режим": mode,
            "Время запуска": logger._core._handlers[0]._sink._file.name if hasattr(logger, '_core') else "N/A"
        })
    except Exception as e:
        logger.error(f"Ошибка отправки Telegram уведомления о запуске: {e}")


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # берём PORT из окружения
    uvicorn.run("main:app", host="0.0.0.0", port=port)
