# src/tests/test_utils.py
from src.utils import round_down
def test_round_down():
    assert round_down(1.234567, "0.0001") == 1.2345
