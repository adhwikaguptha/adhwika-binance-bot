# src/orders/oco_orders.py
from loguru import logger
from ..binance_client import BinanceClient
from ..db import SessionLocal, get_or_create_user, create_order_record

def place_oco_order(
    client: BinanceClient,
    username: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    stop_limit_price: float,
    tif: str = "GTC",
    dry_run: bool = False,
):
    """
    Place an OCO order on Spot (One-Cancels-the-Other).
    Example: Sell BTCUSDT at 30000, but if it drops below 28000, stop-limit at 27950.
    """

    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "quantity": str(quantity),
        "price": str(price),  # main limit order price
        "stopPrice": str(stop_price),  # trigger price for stop
        "stopLimitPrice": str(stop_limit_price),  # price for stop-limit
        "stopLimitTimeInForce": tif,
    }

    logger.info("OCO order params: %s", params)

    db = SessionLocal()
    user = get_or_create_user(db, username)

    if dry_run:
        rec = create_order_record(
            db,
            user.user_id,
            symbol,
            side.upper(),
            price,
            quantity,
            params,
            {"simulated": True},
            "SIMULATED",
        )
        db.close()
        return {"simulated": True, "params": params, "db_order_id": rec.order_id}

    # OCO endpoint works only on Spot
    result = client._request("POST", "/api/v3/order/oco", params=params, signed=True)
    rec = create_order_record(
        db,
        user.user_id,
        symbol,
        side.upper(),
        price,
        quantity,
        params,
        result,
        result.get("orderReports", [{}])[0].get("status", "NEW"),
    )
    db.close()
    return {"api_result": result, "db_order_id": rec.order_id}

# Note: Binance does not support OCO on Futures. The following is an emulation using two separate orders.