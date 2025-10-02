# src/orders/stop_limit_orders.py
from loguru import logger
from ..binance_client import BinanceClient
from ..db import SessionLocal, get_or_create_user, create_order_record

def place_stop_limit_order(
    client: BinanceClient,
    username: str,
    symbol: str,
    side: str,
    stop_price: float,
    limit_price: float,
    quantity: float,
    tif: str = "GTC",
    dry_run: bool = False,
):
    """
    Place a Stop-Limit order.
    Example: Sell BTCUSDT if price drops to 29000, set limit order at 28950.
    """

    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "STOP_LOSS_LIMIT",
        "quantity": str(quantity),
        "price": str(limit_price),
        "stopPrice": str(stop_price),
        "timeInForce": tif,
    }

    logger.info("Stop-Limit order params: %s", params)

    db = SessionLocal()
    user = get_or_create_user(db, username)

    if dry_run:
        rec = create_order_record(
            db,
            user.user_id,
            symbol,
            side.upper(),
            limit_price,
            quantity,
            params,
            {"simulated": True},
            "SIMULATED",
        )
        db.close()
        return {"simulated": True, "params": params, "db_order_id": rec.order_id}

    result = client._request("POST", "/api/v3/order", params=params, signed=True)
    rec = create_order_record(
        db,
        user.user_id,
        symbol,
        side.upper(),
        limit_price,
        quantity,
        params,
        result,
        result.get("status", "NEW"),
    )
    db.close()
    return {"api_result": result, "db_order_id": rec.order_id}
