# src/tests/test_orders.py
from src.orders.market_orders import place_market_order

class DummyClient:
    def exchange_info(self):
        return {"symbols":[{"symbol":"FOO","filters":[{"filterType":"LOT_SIZE","stepSize":"0.001"},{"filterType":"PRICE_FILTER","tickSize":"0.01"}]}]}
    def new_order(self, params):
        return {"orderId": 123, "clientOrderId": "abc", "status": "NEW"}

def test_market_dryrun(tmp_path, monkeypatch):
    # monkeypatch DB to in-memory sqlite for test or use existing DB - here we just simulate API
    client = DummyClient()
    out = place_market_order(client, "testuser", "FOO", "BUY", 0.005, dry_run=True)
    assert out["simulated"] is True
