from fastapi import APIRouter, Request, HTTPException
from loguru import logger
from bot.config import WEBHOOK_SECRET, DEFAULT_EXCHANGE
from bot.db import save_trade, get_last_buy_price, has_previous_buy, get_unsold_quantity, get_exchange_with_coins
from bot.utils import generate_request_id, calculate_qty_by_precision
from bot.exchange_selector import ExchangeSelector
from bot.telegram_notifier import notify_trade, notify_error
from datetime import datetime, timezone

router = APIRouter()
exchange_selector = ExchangeSelector()


@router.post("/webhook")
async def webhook(request: Request):
    try:
    data = await request.json()
    except Exception as e:
        body = await request.body()
        logger.error(f"Ошибка парсинга JSON: {e}")
        logger.error(f"Полученные данные: {body.decode('utf-8')[:500]}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    
    logger.info(f"Сигнал: {data}")

    if data.get("secret") != WEBHOOK_SECRET:
        logger.warning(f"Неверный секрет: получен '{data.get('secret')}', ожидается '{WEBHOOK_SECRET}'")
        raise HTTPException(status_code=403, detail="Access denied")

    side = data.get("action", "").lower()
    if side not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    symbol = data.get("symbol", "BTCUSDT")
    usdt_amount = float(data.get("usdt_amount", 10))
    exchange_name = data.get("exchange", "bybit").lower()  # Берем биржу из сигнала

    # Генерируем уникальный request_id
    request_id = generate_request_id(symbol, side)
    
    logger.info(f"Обработка сигнала: {request_id} на бирже {exchange_name}")

    # Получаем биржу из сигнала (без сравнения цен)
    try:
        exchange = exchange_selector.get_exchange_by_name(exchange_name)
        price = exchange.get_last_price(symbol)
        logger.info(f"🚀 Быстрое выполнение на {exchange.name}: {side} {symbol} по цене {price}")
    except Exception as e:
        error_msg = f"Ошибка получения биржи '{exchange_name}': {e}"
        logger.error(error_msg)
        
        try:
            await notify_error(error_msg, f"Ошибка биржи для {side} {symbol}")
        except Exception as telegram_error:
            logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
        
        return {
            "status": "Error",
            "reason": "Invalid exchange",
            "exchange": exchange_name,
            "symbol": symbol
        }

    # Для продажи проверяем наличие монет на указанной бирже
    if side == "sell":
        coin_symbol = symbol.replace("USDT", "")
        coin_balance = exchange.get_balance(coin_symbol)
        unsold_qty = get_unsold_quantity(exchange.name, symbol)
        
        logger.info(f"Проверка продажи {symbol} на {exchange.name}: баланс={coin_balance:.6f}, непродано={unsold_qty:.6f}")
        
        if coin_balance <= 0 or unsold_qty <= 0:
            error_msg = f"Нет {coin_symbol} для продажи на {exchange.name}. Баланс: {coin_balance:.6f}, непродано: {unsold_qty:.6f}"
            logger.warning(error_msg)
            
            try:
                await notify_error(error_msg, f"Попытка продажи без монет {symbol}")
            except Exception as telegram_error:
                logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
            
            return {
                "status": "Error",
                "reason": "No coins to sell",
                "symbol": symbol,
                "exchange": exchange.name,
                "balance": coin_balance,
                "unsold": unsold_qty
            }

    # Получаем баланс для проверки лимита
    balance_usdt = exchange.get_balance("USDT")

    # Проверка 10% лимита
    if usdt_amount > balance_usdt * 0.1:
        error_msg = f"Сумма сделки ${usdt_amount:.2f} превышает 10% от баланса (${balance_usdt * 0.1:.2f})"
        
        # Отправляем уведомление о превышении лимита в Telegram
        try:
            await notify_error(error_msg, f"Превышение лимита для {side} {symbol}")
        except Exception as telegram_error:
            logger.error(f"Ошибка отправки Telegram уведомления о лимите: {telegram_error}")
        
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
        # При продаже используем количество, которое можно продать (куплено - продано)
        coin_symbol = symbol.replace("USDT", "")
        
        # Получаем количество монет, которое можно продать
        unsold_qty = get_unsold_quantity(exchange.name, symbol)
        coin_balance = exchange.get_balance(coin_symbol)
        
        logger.info(f"Детали для продажи {symbol}: баланс_монет={coin_balance:.6f}, непродано_по_истории={unsold_qty:.6f}")
        
        # Используем минимум из того, что есть на балансе и что было куплено
        available_to_sell = min(coin_balance, unsold_qty)
        
        logger.info(f"Анализ продажи {symbol}: баланс={coin_balance}, куплено-продано={unsold_qty}, доступно={available_to_sell}")
        
        # Проверяем, что есть монеты для продажи
        if available_to_sell <= 0:
            if unsold_qty <= 0:
                error_msg = f"Все {coin_symbol} уже проданы. Нечего продавать."
            else:
                error_msg = f"Нет {coin_symbol} на балансе для продажи. Баланс: {coin_balance}"
            
            logger.warning(error_msg)
            
            # Отправляем уведомление об ошибке в Telegram
            try:
                await notify_error(error_msg, f"Попытка продажи {symbol}")
            except Exception as telegram_error:
                logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
            
            return {
                "status": "Error",
                "reason": "No coins to sell",
                "coin_symbol": coin_symbol,
                "coin_balance": coin_balance,
                "unsold_qty": unsold_qty,
                "available_to_sell": available_to_sell
            }
        
        # Проверяем минимальную сумму сделки (например, $1)
        estimated_value = available_to_sell * price
        if estimated_value < 1.0:
            error_msg = f"Сумма продажи слишком мала: ${estimated_value:.4f} (мин. $1.00)"
            logger.warning(error_msg)
            
            # Отправляем уведомление об ошибке в Telegram
            try:
                await notify_error(error_msg, f"Малая сумма продажи {symbol}")
            except Exception as telegram_error:
                logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")
            
            return {
                "status": "Error",
                "reason": "Amount too small",
                "coin_symbol": coin_symbol,
                "available_to_sell": available_to_sell,
                "estimated_value": estimated_value
            }
        
        qty = available_to_sell
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
        
        # Рассчитываем прибыль только при продаже
        profit = None
        profit_no_fees = None
        if side == "sell":
            last_buy_price = get_last_buy_price(exchange.name, symbol)
            if last_buy_price:
                # Прибыль с учетом комиссий (текущая логика)
                profit = (price - last_buy_price) * qty - fee
                
                # Прибыль БЕЗ комиссий (для анализа стратегии)
                profit_no_fees = (price - last_buy_price) * qty
                
                logger.info(f"Анализ прибыли {symbol}: цена покупки={last_buy_price}, цена продажи={price}")
                logger.info(f"Прибыль БЕЗ комиссий: ${profit_no_fees:.4f}, С комиссиями: ${profit:.4f}, Комиссия: ${fee:.4f}")
        # Для покупок (side == "buy") profit остается None

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
            "profit_no_fees": profit_no_fees,
        "balance_after": balance_after,
        "note": str(result)
    }
    save_trade(trade_data)

        logger.info(f"Сделка выполнена: {request_id} - {side} {qty} {symbol} по {price}")

        # Отправляем уведомление в Telegram
        try:
            await notify_trade(trade_data)
        except Exception as telegram_error:
            logger.error(f"Ошибка отправки Telegram уведомления: {telegram_error}")

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
        
        # Отправляем уведомление об ошибке в Telegram
        try:
            await notify_error(str(e), f"Ошибка при выполнении {side} {symbol}")
        except Exception as telegram_error:
            logger.error(f"Ошибка отправки Telegram уведомления об ошибке: {telegram_error}")
        
        raise HTTPException(status_code=500, detail=str(e))
