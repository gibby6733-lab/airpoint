"""Order execution. PaperExecutor simulates fills against the live order book; LiveExecutor sends real
limit orders and only reports what Kalshi confirms as filled."""
from __future__ import annotations

import asyncio
import logging
import math
import uuid
from dataclasses import dataclass, field

from .config import ExecutionConfig
from .fees import kalshi_fee
from .kalshi_client import KalshiClient, KalshiError
from .models import count_field, price_field

log = logging.getLogger("exec")

NAMESPACE = uuid.UUID("6f1c1a7e-2d0e-4b8a-9c3b-5f0d7e9a1b22")


def client_order_id_for(ticker: str, side: str, mode: str) -> str:
    """Deterministic per market: a retry or restart can never create a second entry order,
    because Kalshi rejects duplicate client_order_ids."""
    return str(uuid.uuid5(NAMESPACE, f"{mode}:{ticker}:{side}:entry"))


@dataclass
class FillResult:
    status: str                 # filled | partial | unfilled | error
    filled: int = 0
    avg_price: float = 0.0
    fees: float = 0.0
    order_id: str | None = None
    client_order_id: str | None = None
    message: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def cost(self) -> float:
        return round(self.filled * self.avg_price + self.fees, 4)


class PaperExecutor:
    mode = "paper"

    def __init__(self, market_data, cfg: ExecutionConfig, sleep=asyncio.sleep):
        self.md = market_data
        self.cfg = cfg
        self.sleep = sleep

    async def buy(self, ticker: str, side: str, contracts: int, limit_price: float, client_order_id: str) -> FillResult:
        if self.cfg.order_style == "ioc":
            book = await self.md.get_orderbook(ticker)
            filled, avg = book.walk(side, contracts, limit_price)
            if filled == 0:
                return FillResult("unfilled", client_order_id=client_order_id, message="no liquidity at limit")
            avg = min(limit_price, avg + self.cfg.paper_extra_slippage)
            fee = kalshi_fee(filled, avg, self.cfg.taker_fee_rate)
            status = "filled" if filled == contracts else "partial"
            return FillResult(status, filled, round(avg, 4), fee, f"paper-{client_order_id[:8]}", client_order_id)
        # passive: rest at the limit; fill if the ask trades down to it within the wait window
        waited = 0.0
        while waited < self.cfg.passive_wait_seconds:
            book = await self.md.get_orderbook(ticker)
            ask = book.best_ask(side)
            if ask is not None and ask <= limit_price + 1e-9:
                filled, _ = book.walk(side, contracts, limit_price)
                fee = kalshi_fee(filled, limit_price, self.cfg.maker_fee_rate)
                return FillResult("filled" if filled == contracts else "partial", filled, limit_price, fee,
                                  f"paper-{client_order_id[:8]}", client_order_id)
            await self.sleep(1.0)
            waited += 1.0
        return FillResult("unfilled", client_order_id=client_order_id, message="passive order not filled in time")

    async def cancel_all(self):
        return 0


class LiveExecutor:
    mode = "live"

    def __init__(self, client: KalshiClient, cfg: ExecutionConfig, price_format: str = "cents", sleep=asyncio.sleep):
        if not client.authenticated:
            raise ValueError("LiveExecutor requires an authenticated Kalshi client")
        self.client = client
        self.cfg = cfg
        self.price_format = price_format
        self.sleep = sleep

    def _order_body(self, ticker, side, contracts, limit_price, client_order_id, tif) -> dict:
        body = {"ticker": ticker, "action": "buy", "side": side, "count": int(contracts), "type": "limit",
                "client_order_id": client_order_id, "time_in_force": tif}
        if self.price_format == "dollars":
            body[f"{side}_price_dollars"] = f"{limit_price:.4f}"
        else:
            body[f"{side}_price"] = int(round(limit_price * 100))
        return body

    async def buy(self, ticker: str, side: str, contracts: int, limit_price: float, client_order_id: str) -> FillResult:
        tif = "immediate_or_cancel" if self.cfg.order_style == "ioc" else "good_till_canceled"
        body = self._order_body(ticker, side, contracts, limit_price, client_order_id, tif)
        order = None
        try:
            resp = await self.client.create_order(body)
            order = resp.get("order", resp)
        except KalshiError as exc:
            if exc.status == 409 or "duplicate" in str(exc).lower():
                order = await self.client.find_order_by_client_id(ticker, client_order_id)
                if order is None:
                    return FillResult("error", client_order_id=client_order_id, message=f"duplicate rejected: {exc}")
            elif exc.status == 0:
                # Network error mid-request: the order may or may not exist. Look it up by client id.
                await self.sleep(1.0)
                order = await self.client.find_order_by_client_id(ticker, client_order_id)
                if order is None:
                    return FillResult("error", client_order_id=client_order_id, message=str(exc))
            else:
                return FillResult("error", client_order_id=client_order_id, message=str(exc))

        order_id = order.get("order_id")
        if self.cfg.order_style == "passive":
            waited = 0.0
            while waited < self.cfg.passive_wait_seconds:
                order = await self.client.get_order(order_id)
                if (order.get("status") or "") in ("executed", "canceled"):
                    break
                await self.sleep(1.0)
                waited += 1.0
            if (order.get("status") or "") == "resting":
                try:
                    await self.client.cancel_order(order_id)
                except KalshiError as exc:
                    log.warning("cancel of %s failed: %s", order_id, exc)
        return await self._confirm_fill(order_id, client_order_id, limit_price)

    async def _confirm_fill(self, order_id: str, client_order_id: str, limit_price: float) -> FillResult:
        """Source of truth = Kalshi's fills for this order (retry a few times for eventual consistency)."""
        fills, order = [], {}
        for _ in range(5):
            try:
                order = await self.client.get_order(order_id)
                fills = await self.client.get_fills(order_id=order_id)
            except KalshiError as exc:
                log.warning("fill confirmation error for %s: %s", order_id, exc)
            filled_order = count_field(order, "fill_count") or 0
            filled_fills = sum(count_field(f, "count") or 0 for f in fills)
            if filled_fills >= filled_order and (order.get("status") in ("executed", "canceled") or filled_fills):
                break
            await self.sleep(1.0)
        filled = int(sum(count_field(f, "count") or 0 for f in fills))
        if filled == 0:
            filled = int(count_field(order, "fill_count") or 0)
        if filled == 0:
            return FillResult("unfilled", order_id=order_id, client_order_id=client_order_id,
                              message=f"order status {order.get('status')}", raw=order)
        side = order.get("side", "yes")
        notional = 0.0
        for f in fills:
            p = price_field(f, f"{side}_price")
            notional += (count_field(f, "count") or 0) * (p if p is not None else limit_price)
        avg = notional / filled if fills else limit_price
        fees = price_field(order, "taker_fees") or 0.0
        fees += price_field(order, "maker_fees") or 0.0
        if fees == 0.0:
            rate = self.cfg.taker_fee_rate if self.cfg.order_style == "ioc" else self.cfg.maker_fee_rate
            fees = kalshi_fee(filled, avg, rate)
        count = count_field(order, "count") or filled
        status = "filled" if filled >= math.floor(count) else "partial"
        return FillResult(status, filled, round(avg, 4), round(fees, 4), order_id, client_order_id, raw=order)

    async def cancel_all(self) -> int:
        n = 0
        for o in await self.client.get_resting_orders():
            try:
                await self.client.cancel_order(o["order_id"])
                n += 1
            except KalshiError as exc:
                log.error("failed to cancel %s: %s", o.get("order_id"), exc)
        return n
