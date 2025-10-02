# src/orders/limit_orders.py
from loguru import logger
from ..binance_client import BinanceClient
from ..utils import parse_symbol_filters, round_down
from ..db import SessionLocal, get_or_create_user, create_order_record

def place_limit_order(client: BinanceClient, username: str, symbol: str, side: str, price: float, quantity: float, tif: str = "GTC", dry_run: bool = False):
    db = SessionLocal()
    user = get_or_create_user(db, username)
    info = client.exchange_info()
    filters = parse_symbol_filters(info, symbol)
    tick = filters["PRICE_FILTER"]["tickSize"]
    step = filters["LOT_SIZE"]["stepSize"]
    p = round_down(price, tick)
    q = round_down(quantity, step)
    if q <= 0:
        raise ValueError("quantity rounds to zero")
    params = {"symbol": symbol, "side": side.upper(), "type": "LIMIT", "timeInForce": tif, "price": str(p), "quantity": str(q)}
    logger.info("Limit order params: %s", params)
    if dry_run:
        rec = create_order_record(db, user.user_id, symbol, side.upper(), p, q, params, {"simulated": True}, "SIMULATED")
        db.close()
        return {"simulated": True, "params": params, "db_record": {"order_id": rec.order_id}}
    res = client.new_order(params)
    status = res.get("status") or "NEW"
    rec = create_order_record(db, user.user_id, symbol, side.upper(), p, q, params, res, status)
    db.close()
    return {"api_result": res, "db_order_id": rec.order_id}
