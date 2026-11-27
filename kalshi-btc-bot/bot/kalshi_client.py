"""Kalshi Trade API v2 client.

Auth: each private request carries
  KALSHI-ACCESS-KEY        key id
  KALSHI-ACCESS-TIMESTAMP  ms since epoch
  KALSHI-ACCESS-SIGNATURE  base64(RSA-PSS-SHA256(timestamp + METHOD + path_without_query))
Market data endpoints are public, so paper trading needs no credentials.
The private key is only ever held in this process; it is never logged or sent to the dashboard.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import random
import time
from typing import Any

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .config import API_PREFIX
from .models import Market, OrderBook, parse_market, parse_orderbook

log = logging.getLogger("kalshi")


class KalshiError(Exception):
    def __init__(self, status: int, message: str, body: Any = None):
        super().__init__(f"Kalshi HTTP {status}: {message}")
        self.status = status
        self.body = body


class KalshiSigner:
    def __init__(self, key_id: str, private_key_pem: bytes):
        self.key_id = key_id
        self._key = serialization.load_pem_private_key(private_key_pem, password=None)

    def headers(self, method: str, path: str, ts_ms: int | None = None) -> dict:
        ts = str(ts_ms if ts_ms is not None else int(time.time() * 1000))
        path_no_query = path.split("?")[0]
        msg = (ts + method.upper() + path_no_query).encode()
        sig = self._key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256(),
        )
        return {
            "KALSHI-ACCESS-KEY": self.key_id,
            "KALSHI-ACCESS-TIMESTAMP": ts,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
        }


class KalshiClient:
    RETRY_STATUSES = {429, 500, 502, 503, 504}

    def __init__(self, base_url: str, signer: KalshiSigner | None = None, timeout: float = 10.0,
                 max_retries: int = 4, transport: httpx.AsyncBaseTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.signer = signer
        self.max_retries = max_retries
        self._http = httpx.AsyncClient(base_url=self.base_url, timeout=timeout, transport=transport,
                                       headers={"Accept": "application/json", "User-Agent": "btc15m-momentum-bot/1.0"})
        self._min_interval = 0.06  # stay well under rate limits
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def close(self):
        await self._http.aclose()

    @property
    def authenticated(self) -> bool:
        return self.signer is not None

    async def request(self, method: str, endpoint: str, *, params: dict | None = None,
                      json: dict | None = None, auth: bool = False, retry: bool = True) -> dict:
        path = API_PREFIX + endpoint
        attempt = 0
        while True:
            async with self._lock:
                wait = self._min_interval - (time.monotonic() - self._last_call)
                if wait > 0:
                    await asyncio.sleep(wait)
                self._last_call = time.monotonic()
            headers = {}
            if auth:
                if not self.signer:
                    raise KalshiError(401, "credentials required for this endpoint")
                headers.update(self.signer.headers(method, path))
            try:
                resp = await self._http.request(method, path, params=params, json=json, headers=headers)
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if not retry or attempt >= self.max_retries:
                    raise KalshiError(0, f"network error: {exc}") from exc
                attempt += 1
                delay = min(8.0, 0.5 * 2 ** attempt) + random.random() * 0.25
                log.warning("Kalshi %s %s network error (%s); retry %d in %.1fs", method, endpoint, exc, attempt, delay)
                await asyncio.sleep(delay)
                continue
            if resp.status_code in self.RETRY_STATUSES and retry and attempt < self.max_retries:
                attempt += 1
                delay = min(8.0, 0.5 * 2 ** attempt) + random.random() * 0.25
                log.warning("Kalshi %s %s -> %d; retry %d in %.1fs", method, endpoint, resp.status_code, attempt, delay)
                await asyncio.sleep(delay)
                continue
            if resp.status_code >= 400:
                try:
                    body = resp.json()
                except ValueError:
                    body = resp.text
                msg = body.get("error", {}).get("message", str(body)) if isinstance(body, dict) else str(body)
                raise KalshiError(resp.status_code, msg, body)
            if not resp.content:
                return {}
            return resp.json()

    # ------------------------------------------------------------ market data (public)

    async def get_markets(self, series_ticker: str, status: str | None = None, limit: int = 100,
                          cursor: str | None = None, **extra) -> dict:
        params = {"series_ticker": series_ticker, "limit": limit, **extra}
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
        return await self.request("GET", "/markets", params=params)

    async def list_markets(self, series_ticker: str, up_side: str, status: str | None = "open") -> list[Market]:
        data = await self.get_markets(series_ticker, status=status)
        return [parse_market(m, up_side) for m in data.get("markets", [])]

    async def get_market(self, ticker: str, up_side: str = "yes") -> Market:
        data = await self.request("GET", f"/markets/{ticker}")
        return parse_market(data.get("market", data), up_side)

    async def get_orderbook(self, ticker: str, depth: int = 20) -> OrderBook:
        data = await self.request("GET", f"/markets/{ticker}/orderbook", params={"depth": depth})
        return parse_orderbook(data, ts=time.time())

    async def get_market_candlesticks(self, series_ticker: str, ticker: str, start_ts: int, end_ts: int,
                                      period_interval: int = 1) -> list[dict]:
        data = await self.request(
            "GET", f"/series/{series_ticker}/markets/{ticker}/candlesticks",
            params={"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_interval})
        return data.get("candlesticks", [])

    async def get_exchange_status(self) -> dict:
        return await self.request("GET", "/exchange/status")

    # ------------------------------------------------------------ portfolio (authenticated)

    async def get_balance(self) -> float:
        data = await self.request("GET", "/portfolio/balance", auth=True)
        if "balance_dollars" in data:
            return float(data["balance_dollars"])
        return float(data.get("balance", 0)) / 100.0

    async def create_order(self, body: dict) -> dict:
        # Never auto-retry order creation on network errors without idempotency; client_order_id
        # makes a retry safe because Kalshi rejects duplicates, but we still retry only once.
        return await self.request("POST", "/portfolio/orders", json=body, auth=True, retry=False)

    async def get_order(self, order_id: str) -> dict:
        data = await self.request("GET", f"/portfolio/orders/{order_id}", auth=True)
        return data.get("order", data)

    async def find_order_by_client_id(self, ticker: str, client_order_id: str) -> dict | None:
        data = await self.request("GET", "/portfolio/orders", params={"ticker": ticker, "limit": 100}, auth=True)
        for o in data.get("orders", []):
            if o.get("client_order_id") == client_order_id:
                return o
        return None

    async def cancel_order(self, order_id: str) -> dict:
        return await self.request("DELETE", f"/portfolio/orders/{order_id}", auth=True)

    async def get_fills(self, order_id: str | None = None, ticker: str | None = None) -> list[dict]:
        params = {"limit": 200}
        if order_id:
            params["order_id"] = order_id
        if ticker:
            params["ticker"] = ticker
        data = await self.request("GET", "/portfolio/fills", params=params, auth=True)
        return data.get("fills", [])

    async def get_resting_orders(self) -> list[dict]:
        data = await self.request("GET", "/portfolio/orders", params={"status": "resting", "limit": 200}, auth=True)
        return data.get("orders", [])

    async def get_positions(self) -> dict:
        return await self.request("GET", "/portfolio/positions", auth=True)


def build_client(cfg) -> KalshiClient:
    signer = None
    if cfg.secrets.has_kalshi_credentials():
        pem = cfg.secrets.load_private_key_pem()
        signer = KalshiSigner(cfg.secrets.kalshi_key_id, pem)
    return KalshiClient(cfg.kalshi.base_url, signer=signer)
