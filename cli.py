import os
import sys
import argparse
from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import OrderRequest, place_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from bot.exceptions import ValidationError, ApiError, NetworkError, BotError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trading-bot",
        description="Simplified Binance Futures Testnet Trading Bot (USDT-M)",
    )
    p.add_argument("--log-file", default="logs/bot.log", help="Log file path (default: logs/bot.log)")
    p.add_argument("--base-url", default="https://testnet.binancefuture.com", help="Testnet base URL")

    p.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    p.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    p.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type",
    )
    p.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.001")

    p.add_argument("--price", help="Required for LIMIT and STOP_LIMIT")
    p.add_argument("--stop-price", help="Required for STOP_LIMIT (trigger price)")

    return p


def print_summary(req: OrderRequest) -> None:
    print("\n=== Order Request Summary ===")
    print(f"Symbol      : {req.symbol}")
    print(f"Side        : {req.side}")
    print(f"Type        : {req.order_type}")
    print(f"Quantity    : {req.quantity}")
    if req.price is not None:
        print(f"Price       : {req.price}")
    if req.stop_price is not None:
        print(f"Stop Price  : {req.stop_price}")
    print("============================\n")


def print_response(resp: dict) -> None:
    print("=== Order Response ===")
    # Common Futures fields:
    # orderId, status, executedQty, avgPrice (sometimes), price, origQty
    order_id = resp.get("orderId") or resp.get("clientOrderId")
    print(f"orderId     : {order_id}")
    print(f"status      : {resp.get('status')}")
    print(f"executedQty : {resp.get('executedQty')}")
    # avgPrice may be present in some response types; try a few keys
    avg_price = resp.get("avgPrice") or resp.get("averagePrice")
    if avg_price is not None:
        print(f"avgPrice    : {avg_price}")
    print(f"raw         : {resp}")
    print("======================\n")


def main() -> int:
    load_dotenv()  # allow reading BINANCE_API_KEY and BINANCE_API_SECRET from .env

    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log_file)

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print("ERROR: Missing BINANCE_API_KEY or BINANCE_API_SECRET in environment/.env", file=sys.stderr)
        return 2

    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.type)
        quantity = validate_quantity(args.quantity)

        price_required = order_type in ("LIMIT", "STOP_LIMIT")
        stop_required = order_type == "STOP_LIMIT"

        price = validate_price(args.price, required=price_required)
        stop_price = validate_stop_price(args.stop_price, required=stop_required)

        req = OrderRequest(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        print_summary(req)

        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=args.base_url,
            logger=logger,
        )

        resp = place_order(client, req)
        print_response(resp)

        print("✅ SUCCESS: Order placed successfully.")
        return 0

    except ValidationError as e:
        logger.error("Validation error: %s", str(e))
        print(f"❌ INPUT ERROR: {e}", file=sys.stderr)
        return 2

    except ApiError as e:
        logger.error("API error: %s | status=%s payload=%s", str(e), e.status_code, e.payload)
        print(f"❌ API ERROR: {e}", file=sys.stderr)
        if e.payload:
            print(f"Details: {e.payload}", file=sys.stderr)
        return 3

    except NetworkError as e:
        logger.error("Network error: %s", str(e))
        print(f"❌ NETWORK ERROR: {e}", file=sys.stderr)
        return 4

    except BotError as e:
        logger.exception("Bot error: %s", str(e))
        print(f"❌ ERROR: {e}", file=sys.stderr)
        return 5

    except Exception as e:
        logger.exception("Unexpected error: %s", str(e))
        print(f"❌ UNEXPECTED ERROR: {e}", file=sys.stderr)
        return 99


if __name__ == "__main__":
    raise SystemExit(main())
===
