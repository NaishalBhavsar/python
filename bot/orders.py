from dataclasses import dataclass
from typing import Any

from .client import BinanceFuturesClient


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: str
    order_type: str  # MARKET / LIMIT / STOP_LIMIT
    quantity: float
    price: float | None = None
    stop_price: float | None = None


def place_order(client: BinanceFuturesClient, req: OrderRequest) -> dict[str, Any]:
    """
    Places an order on USDT-M Futures testnet.

    Endpoint:
      POST /fapi/v1/order  (SIGNED)
    """
    params: dict[str, Any] = {
        "symbol": req.symbol,
        "side": req.side,
        "type": req.order_type if req.order_type != "STOP_LIMIT" else "STOP",
        "quantity": req.quantity,
        "newOrderRespType": "RESULT",  # gives more details if available
    }

    if req.order_type == "LIMIT":
        params.update(
            {
                "timeInForce": "GTC",
                "price": req.price,
            }
        )

    if req.order_type == "STOP_LIMIT":
        # Binance Futures uses type=STOP with stopPrice + price + timeInForce for stop-limit
        params.update(
            {
                "timeInForce": "GTC",
                "price": req.price,
                "stopPrice": req.stop_price,
                "workingType": "CONTRACT_PRICE",
            }
        )

    return client.request("POST", "/fapi/v1/order", params=params, signed=True)
