# src/utils.py
from decimal import Decimal, getcontext
getcontext().prec = 28

def _dec(x): return Decimal(str(x))

def round_down(value, step):
    """
    Round down 'value' to the multiple of 'step' (tickSize / stepSize).
    """
    v = _dec(value)
    s = _dec(step)
    quant = (v // s) * s
    return float(quant)

def parse_symbol_filters(exchange_info: dict, symbol: str):
    for s in exchange_info.get("symbols", []):
        if s["symbol"] == symbol:
            return {f["filterType"]: f for f in s["filters"]}
    raise ValueError(f"Symbol {symbol} not found in exchange info")
