import requests, time, hmac, hashlib, os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    raise RuntimeError("API keys not loaded from .env")

API_SECRET = API_SECRET.encode()

def signed_request(base_url, path="/fapi/v2/account"):
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = hmac.new(API_SECRET, query.encode(), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": API_KEY}
    url = f"{base_url}{path}?{query}&signature={signature}"
    r = requests.get(url, headers=headers)
    return r.status_code, r.text

# Testnet
status, body = signed_request("https://testnet.binancefuture.com")
print("\nChecking Testnet...")
print("Status:", status)
print("Body:", body[:200], "...")

# Mainnet
status, body = signed_request("https://fapi.binance.com")
print("\nChecking Mainnet...")
print("Status:", status)
print("Body:", body[:200], "...")
