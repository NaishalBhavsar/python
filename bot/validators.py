import re
from .exceptions import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}  # STOP_LIMIT is optional bonus


def validate_symbol(symbol: str) -> str:
    if not symbol:
        raise ValidationError("symbol is required")
    s = symbol.strip().upper()
    # Binance symbols are usually uppercase alnum, e.g. BTCUSDT
    if not re.fullmatch(r"[A-Z0-9]{6,20}", s):
        raise ValidationError("symbol must look like BTCUSDT (uppercase alphanumeric, 6–20 chars)")
    return s


def validate_side(side: str) -> str:
    if not side:
        raise ValidationError("side is required (BUY/SELL)")
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    return s


def validate_order_type(order_type: str) -> str:
    if not order_type:
        raise ValidationError("order type is required (MARKET/LIMIT/STOP_LIMIT)")
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET, LIMIT, or STOP_LIMIT")
    return t


def validate_quantity(qty: str) -> float:
    try:
        value = float(qty)
    except ValueError:
        raise ValidationError("quantity must be a number")

    if value <= 0:
        raise ValidationError("quantity must be > 0")
    return value


def validate_price(price: str | None, required: bool) -> float | None:
    if price is None:
        if required:
            raise ValidationError("price is required for this order type")
        return None

    try:
        value = float(price)
    except ValueError:
        raise ValidationError("price must be a number")

    if value <= 0:
        raise ValidationError("price must be > 0")
    return value


def validate_stop_price(stop_price: str | None, required: bool) -> float | None:
    if stop_price is None:
        if required:
            raise ValidationError("stop-price is required for STOP_LIMIT orders")
        return None

    try:
        value = float(stop_price)
    except ValueError:
        raise ValidationError("stop-price must be a number")

    if value <= 0:
        raise ValidationError("stop-price must be > 0")
    return value
