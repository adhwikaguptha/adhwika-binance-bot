# src/advanced/twap_strategy.py
import time, random
from loguru import logger
from ..utils import parse_symbol_filters, round_down

def twap(client, symbol, side, total_qty, slices=10, interval_seconds=60, jitter_pct=0.2, dry_run=False):
    info = client.exchange_info()
    filters = parse_symbol_filters(info, symbol)
    step = filters["LOT_SIZE"]["stepSize"]
    qty_each = total_qty / slices
    qty_each = round_down(qty_each, step)
    remaining = total_qty
    results = []
    for i in range(slices):
        if remaining <= 0: break
        q = min(qty_each, remaining)
        if q <= 0: break
        logger.info("TWAP slice %d/%d qty=%s", i+1, slices, q)
        if dry_run:
            results.append({"slice": i+1, "simulated": True, "qty": q})
        else:
            res = client.new_order({"symbol": symbol, "side": side.upper(), "type": "MARKET", "quantity": str(q)})
            results.append(res)
        remaining -= q
        sleep_sec = max(0.5, interval_seconds + (random.random() - 0.5)*jitter_pct*interval_seconds)
        time.sleep(sleep_sec)
    return results
