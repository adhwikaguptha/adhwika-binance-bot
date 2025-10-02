# src/binance_client.py
import time, hmac, hashlib
from urllib.parse import urlencode
import requests
from requests.adapters import HTTPAdapter, Retry
from loguru import logger
from .config import API_KEY, API_SECRET, BASE_URL, TRADING_MODE
from typing import Dict, Any, Optional

class BinanceError(Exception):
    pass

class BinanceClient:
    def __init__(self, api_key: str = API_KEY, api_secret: str = API_SECRET, base_url: str = BASE_URL, timeout: int = 10):
        self.api_key = api_key
        self.api_secret = api_secret.encode() if api_secret else None
        self.base = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=4, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _sign(self, params: Dict[str, Any]) -> str:
        qs = urlencode(params)
        return hmac.new(self.api_secret, qs.encode(), hashlib.sha256).hexdigest()

    def _request(self, method: str, path: str, params: Dict[str, Any] = None, signed: bool = False):
        url = self.base + path
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        params = params or {}
        if signed:
            params.update({"timestamp": int(time.time() * 1000)})
            params["signature"] = self._sign(params)
        if method == "GET":
            r = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        else:
            r = self.session.post(url, data=params, headers=headers, timeout=self.timeout)
        try:
            data = r.json()
        except ValueError:
            r.raise_for_status()
            raise BinanceError("Non-JSON response")
        if r.status_code >= 400 or (isinstance(data, dict) and data.get("code")):
            raise BinanceError(data)
        return data

    # Public endpoints
    def ping(self):
        return self._request("GET", "/api/v3/ping" if TRADING_MODE.startswith("spot") else "/fapi/v1/ping")

    def time(self):
        return self._request("GET", "/api/v3/time" if TRADING_MODE.startswith("spot") else "/fapi/v1/time")

    def exchange_info(self):
        return self._request("GET", "/api/v3/exchangeInfo" if TRADING_MODE.startswith("spot") else "/fapi/v1/exchangeInfo")

    # Place order
    def new_order(self, params: Dict[str, Any]):
        if TRADING_MODE.startswith("spot"):
            return self._request("POST", "/api/v3/order", params=params, signed=True)
        else:
            return self._request("POST", "/fapi/v1/order", params=params, signed=True)
   