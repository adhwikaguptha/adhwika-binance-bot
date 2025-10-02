# src/advanced/grid_strategy.py
from loguru import logger
from ..utils import round_down, parse_symbol_filters

def create_grid(client, symbol, lower, upper, levels, qty_per_order, dry_run=False):
    info = client.exchange_info()
    filters = parse_symbol_filters(info, symbol)
    tick = float(filters["PRICE_FILTER"]["tickSize"])
    step = float(filters["LOT_SIZE"]["stepSize"])
    spacing = (upper - lower) / float(levels)
    orders = []
    for i in range(levels + 1):
        price = lower + i * spacing
        price = round_down(price, tick)
        q = round_down(qty_per_order, step)
        if q <= 0:
            raise ValueError("quantity rounds to zero; increase qty_per_order")
        params = {"symbol": symbol, "side": "BUY" if i <= levels/2 else "SELL", "type": "LIMIT", "timeInForce":"GTC", "price": str(price), "quantity": str(q)}
        logger.info("Grid order params: %s", params)
        if dry_run:
            orders.append({"simulated": True, "params": params})
        else:
            orders.append(client.new_order(params))
    return orders
