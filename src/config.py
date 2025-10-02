# src/config.py
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TRADING_MODE = os.getenv("TRADING_MODE", "spot_testnet")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/bot_bd")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if TRADING_MODE == "spot_testnet":
    BASE_URL = os.getenv("SPOT_TESTNET_BASE")
    WS_URL = os.getenv("SPOT_TESTNET_WS")
elif TRADING_MODE == "futures_testnet":
    BASE_URL = os.getenv("FAPI_BASE_TESTNET")
    WS_URL = os.getenv("WS_BASE_TESTNET")
elif TRADING_MODE == "futures_mainnet":
    BASE_URL = os.getenv("FAPI_BASE_LIVE")
    WS_URL = os.getenv("WS_BASE_LIVE")
else:
    raise ValueError(f"Unknown TRADING_MODE={TRADING_MODE}")
