from datetime import datetime
from decimal import Decimal, ROUND_DOWN


def generate_request_id(symbol, side):
    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{now}_{symbol}_{side}".upper()


def calculate_qty_by_precision(usdt_amount, price, precision=6):
    """
    Рассчитывает количество монет с учётом precision биржи
    """
    qty = usdt_amount / price
    # Округляем до precision знаков после запятой
    decimal_qty = Decimal(str(qty))
    rounded_qty = decimal_qty.quantize(
        Decimal('0.' + '0' * precision),
        rounding=ROUND_DOWN
    )
    return float(rounded_qty)


def calculate_fee_for_buy(balance_before, balance_after, deal_value, price):
    """
    Расчёт комиссии для покупки:
    стоимость монет в сделке - баланс монет после сделки * цена
    """
    coins_after = balance_after / price
    coins_in_deal = deal_value / price
    fee_coins = coins_in_deal - coins_after
    return fee_coins * price


def calculate_fee_for_sell(balance_before, balance_after, deal_value):
    """
    Расчёт комиссии для продажи:
    средства на счете перед сделкой + стоимость сделки - баланс после сделки
    """
    return balance_before + deal_value - balance_after
