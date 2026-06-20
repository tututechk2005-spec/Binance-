import hmac
import hashlib
import time
from typing import Optional, Dict, Any
import httpx
from loguru import logger
from core.config import settings
from core.security import decrypt_api_key
from database.models import NetworkType


class BinanceClient:
    BASE_URLS = {
        NetworkType.SPOT_MAINNET: settings.BINANCE_SPOT_MAINNET_BASE_URL,
        NetworkType.FUTURES_MAINNET: settings.BINANCE_FUTURES_MAINNET_BASE_URL,
        NetworkType.SPOT_TESTNET: settings.BINANCE_SPOT_TESTNET_BASE_URL,
        NetworkType.FUTURES_TESTNET: settings.BINANCE_FUTURES_TESTNET_BASE_URL,
    }

    def __init__(self, encrypted_api_key: str, encrypted_secret_key: str, network_type: NetworkType):
        self.api_key = decrypt_api_key(encrypted_api_key)
        self.secret_key = decrypt_api_key(encrypted_secret_key)
        self.network_type = network_type
        self.base_url = self.BASE_URLS[network_type]
        self.is_futures = "FUTURES" in network_type.value.upper()

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = "&".join(f"{k}={v}" for k, v in params.items())
        signature = hmac.new(
            self.secret_key.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _headers(self) -> dict:
        return {"X-MBX-APIKEY": self.api_key, "Content-Type": "application/json"}

    async def _get(self, endpoint: str, params: dict = None, signed: bool = False) -> dict:
        if params is None:
            params = {}
        if signed:
            params = self._sign(params)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}{endpoint}", params=params, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def _post(self, endpoint: str, params: dict = None, signed: bool = True) -> dict:
        if params is None:
            params = {}
        if signed:
            params = self._sign(params)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}{endpoint}", params=params, headers=self._headers()
            )
            resp.raise_for_status()
            return resp.json()

    async def _delete(self, endpoint: str, params: dict = None, signed: bool = True) -> dict:
        if params is None:
            params = {}
        if signed:
            params = self._sign(params)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.delete(
                f"{self.base_url}{endpoint}", params=params, headers=self._headers()
            )
            resp.raise_for_status()
            return resp.json()

    async def get_account_info(self) -> dict:
        endpoint = "/fapi/v2/account" if self.is_futures else "/api/v3/account"
        return await self._get(endpoint, signed=True)

    async def get_exchange_info(self, symbol: Optional[str] = None) -> dict:
        endpoint = "/fapi/v1/exchangeInfo" if self.is_futures else "/api/v3/exchangeInfo"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._get(endpoint, params=params)

    async def get_ticker_price(self, symbol: str) -> dict:
        endpoint = "/fapi/v1/ticker/price" if self.is_futures else "/api/v3/ticker/price"
        return await self._get(endpoint, params={"symbol": symbol})

    async def get_all_tickers(self) -> list:
        endpoint = "/fapi/v1/ticker/price" if self.is_futures else "/api/v3/ticker/price"
        return await self._get(endpoint)

    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> list:
        endpoint = "/fapi/v1/klines" if self.is_futures else "/api/v3/klines"
        return await self._get(endpoint, params={"symbol": symbol, "interval": interval, "limit": limit})

    async def get_order_book(self, symbol: str, limit: int = 20) -> dict:
        endpoint = "/fapi/v1/depth" if self.is_futures else "/api/v3/depth"
        return await self._get(endpoint, params={"symbol": symbol, "limit": limit})

    async def get_open_orders(self, symbol: Optional[str] = None) -> list:
        endpoint = "/fapi/v1/openOrders" if self.is_futures else "/api/v3/openOrders"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._get(endpoint, params=params, signed=True)

    async def get_all_orders(self, symbol: str, limit: int = 100) -> list:
        endpoint = "/fapi/v1/allOrders" if self.is_futures else "/api/v3/allOrders"
        return await self._get(endpoint, params={"symbol": symbol, "limit": limit}, signed=True)

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
        close_position: bool = False,
        activation_price: Optional[float] = None,
        callback_rate: Optional[float] = None,
        working_type: str = "MARK_PRICE",
    ) -> dict:
        endpoint = "/fapi/v1/order" if self.is_futures else "/api/v3/order"
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price and order_type in ("LIMIT", "STOP", "STOP_LIMIT"):
            params["price"] = price
            params["timeInForce"] = time_in_force
        if stop_price:
            params["stopPrice"] = stop_price
        if self.is_futures:
            if reduce_only:
                params["reduceOnly"] = "true"
            if close_position:
                params["closePosition"] = "true"
            if order_type == "TRAILING_STOP_MARKET":
                params["callbackRate"] = callback_rate
                if activation_price:
                    params["activationPrice"] = activation_price
                params["workingType"] = working_type
        return await self._post(endpoint, params=params)

    async def cancel_order(self, symbol: str, order_id: int) -> dict:
        endpoint = "/fapi/v1/order" if self.is_futures else "/api/v3/order"
        return await self._delete(endpoint, params={"symbol": symbol, "orderId": order_id})

    async def cancel_all_orders(self, symbol: str) -> dict:
        endpoint = "/fapi/v1/allOpenOrders" if self.is_futures else "/api/v3/openOrders"
        return await self._delete(endpoint, params={"symbol": symbol})

    async def get_positions(self) -> list:
        if not self.is_futures:
            return []
        return await self._get("/fapi/v2/positionRisk", signed=True)

    async def set_leverage(self, symbol: str, leverage: int) -> dict:
        if not self.is_futures:
            return {}
        return await self._post("/fapi/v1/leverage", params={"symbol": symbol, "leverage": leverage})

    async def set_margin_type(self, symbol: str, margin_type: str) -> dict:
        if not self.is_futures:
            return {}
        return await self._post("/fapi/v1/marginType", params={"symbol": symbol, "marginType": margin_type})

    async def get_income_history(self, income_type: Optional[str] = None, limit: int = 100) -> list:
        if not self.is_futures:
            return []
        params: Dict[str, Any] = {"limit": limit}
        if income_type:
            params["incomeType"] = income_type
        return await self._get("/fapi/v1/income", params=params, signed=True)

    async def validate_credentials(self) -> bool:
        try:
            await self.get_account_info()
            return True
        except Exception as e:
            logger.warning(f"Credential validation failed: {e}")
            return False

    async def get_my_trades(self, symbol: str, limit: int = 50) -> list:
        endpoint = "/fapi/v1/userTrades" if self.is_futures else "/api/v3/myTrades"
        return await self._get(endpoint, params={"symbol": symbol, "limit": limit}, signed=True)

    async def get_24hr_ticker(self, symbol: str) -> dict:
        endpoint = "/fapi/v1/ticker/24hr" if self.is_futures else "/api/v3/ticker/24hr"
        return await self._get(endpoint, params={"symbol": symbol})

    async def get_balance(self) -> list:
        if self.is_futures:
            return await self._get("/fapi/v2/balance", signed=True)
        account = await self.get_account_info()
        return account.get("balances", [])
