from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from bot.db import init_db, init_test_balances
from bot.webhook import router as webhook_router
from bot.exchanges.bybit import BybitExchange
from bot.exchanges.binance import BinanceExchange
from bot.config import TEST_MODE
from bot.telegram_notifier import notify_status
import uvicorn
import os

# Инициализируем экземпляры бирж
bybit = BybitExchange()
binance = BinanceExchange()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
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
    
    # Настраиваем Telegram webhook (если нужно)
    try:
        from bot.telegram_bot import setup_telegram_webhook
        webhook_setup = await setup_telegram_webhook()
        if webhook_setup:
            logger.info("Telegram webhook настроен")
    except Exception as e:
        logger.error(f"Ошибка настройки Telegram webhook: {e}")
    
    # Отправляем уведомление о запуске в Telegram
    try:
        await notify_status("Бот запущен и готов к работе", {
            "Режим": mode,
            "Время запуска": "N/A"
        })
    except Exception as e:
        logger.error(f"Ошибка отправки Telegram уведомления: {e}")
    
    yield
    
    # Shutdown
    logger.info("Бот завершает работу")


app = FastAPI(lifespan=lifespan)


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


@app.get("/profit")
def get_profit():
    """Получить статистику прибыли"""
    from bot.db import get_profit_statistics
    profit_stats = get_profit_statistics()
    return {"profit": profit_stats}


@app.post("/telegram-webhook")
async def telegram_webhook_post(update: dict):
    """Webhook для обработки команд от Telegram"""
    from bot.telegram_bot import process_telegram_update
    logger.info(f"Получен POST запрос на telegram-webhook: {update}")
    try:
        success = await process_telegram_update(update)
        return {"ok": success}
    except Exception as e:
        logger.error(f"Ошибка обработки Telegram webhook: {e}")
        return {"ok": False, "error": str(e)}


@app.get("/telegram-webhook")
async def telegram_webhook_get():
    """GET endpoint для проверки webhook Telegram"""
    logger.info("Получен GET запрос на telegram-webhook (проверка)")
    return {"status": "ok", "message": "Telegram webhook is active"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # берём PORT из окружения
    uvicorn.run("main:app", host="0.0.0.0", port=port)
