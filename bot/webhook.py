from fastapi import APIRouter, Request, HTTPException
from loguru import logger
from bot.config import WEBHOOK_SECRET, DEFAULT_EXCHANGE
from bot.db import save_trade, get_last_buy_price
from bot.utils import generate_request_id, calculate_qty_by_precision
from bot.exchange_selector import ExchangeSelector
from datetime import datetime, timezone

router = APIRouter()
exchange_selector = ExchangeSelector()


@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logger.info(f"Сигнал: {data}")

    if data.get("secret") != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Access denied")

    side = data.get("action", "").lower()
    if side not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    symbol = data.get("symbol", "BTCUSDT")
    usdt_amount = float(data.get("usdt_amount", 10))

    # Определяем биржу
    if side == "buy":
        # Для покупки выбираем биржу с лучшей ценой и достаточными средствами
        exchange, price = exchange_selector.get_best_price_exchange(symbol, usdt_amount)
        logger.info(f"Выбрана биржа {exchange.name} для покупки по цене {price}")
    else:
        # Для продажи используем биржу из сигнала или по умолчанию
        exchange_name = data.get("exchange", DEFAULT_EXCHANGE).lower()
        exchange = exchange_selector.get_exchange_by_name(exchange_name)
        price = exchange.get_last_price(symbol)
        logger.info(f"Используем биржу {exchange.name} для продажи по цене {price}")

    # Получаем баланс для проверки лимита
    balance_usdt = exchange.get_balance("USDT")

    # Проверка 10% лимита
    if usdt_amount > balance_usdt * 0.1:
        return {
            "status": "Error",
            "reason": "Amount exceeds 10% of balance",
            "balance": balance_usdt,
            "max_amount": balance_usdt * 0.1
        }

    # Рассчитываем количество с учётом precision
    if side == "buy":
        qty = calculate_qty_by_precision(usdt_amount, price, 6)
        market_unit = "quoteCoin" if exchange.name == "Bybit" else None
    else:
        # При продаже используем весь доступный баланс монеты
        coin_symbol = symbol.replace("USDT", "")
        coin_balance = exchange.get_balance(coin_symbol)
        qty = coin_balance
        market_unit = "baseCoin" if exchange.name == "Bybit" else None

    # Генерируем request_id
    request_id = generate_request_id(symbol, side)

    try:
        # Исполнение ордера
        result = exchange.place_order(side, symbol, qty, market_unit)
        
        # Получаем обновлённый баланс
        balance_after = exchange.get_balance("USDT")
        
        # Комиссия уже рассчитана в place_order
        fee = result.get("fee", 0.0) if isinstance(result, dict) else 0.0
        
        # Рассчитываем прибыль при продаже
        profit = None
        if side == "sell":
            last_buy_price = get_last_buy_price(exchange.name, symbol)
            if last_buy_price:
                profit = (price - last_buy_price) * qty - fee

        # Сохраняем сделку
        trade_data = {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exchange": exchange.name,
            "side": side,
            "symbol": symbol,
            "price": price,
            "qty": qty,
            "amount_usdt": usdt_amount if side == "buy" else qty * price,
            "fee": fee,
            "profit": profit,
            "balance_after": balance_after,
            "note": str(result)
        }
        save_trade(trade_data)

        logger.info(f"Сделка выполнена: {request_id} - {side} {qty} {symbol} по {price}")

        return {
            "status": "ok", 
            "request_id": request_id,
            "exchange": exchange.name,
            "order": result, 
            "balance_after": balance_after,
            "profit": profit
        }

    except Exception as e:
        logger.error(f"Ошибка выполнения сделки: {e}")
        raise HTTPException(status_code=500, detail=str(e))
