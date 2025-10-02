# src/orders/market_orders.py
import uuid
from loguru import logger
from ..binance_client import BinanceClient
from ..utils import parse_symbol_filters, round_down
from ..db import SessionLocal, get_or_create_user, create_order_record

def place_market_order(client: BinanceClient, username: str, symbol: str, side: str, quantity: float, dry_run: bool = False):
    db = SessionLocal()
    user = get_or_create_user(db, username)
    info = client.exchange_info()
    filters = parse_symbol_filters(info, symbol)
    step = filters["LOT_SIZE"]["stepSize"]
    q = round_down(quantity, step)
    if q <= 0:
        raise ValueError("quantity rounds to zero; increase size")
    params = {"symbol": symbol, "side": side.upper(), "type": "MARKET", "quantity": str(q)}
    logger.info("Market order params: %s", params)
    if dry_run:
        # store simulated signal record
        rec = create_order_record(db, user.user_id, symbol, side.upper(), None, q, params, {"simulated": True}, "SIMULATED")
        db.close()
        return {"simulated": True, "params": params, "db_record": {"order_id": rec.order_id}}
    # attempt API call
    res = client.new_order(params)
    status = res.get("status") or "NEW"
    rec = create_order_record(db, user.user_id, symbol, side.upper(), None, q, params, res, status)
    db.close()
    return {"api_result": res, "db_order_id": rec.order_id}
