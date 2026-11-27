"""Kalshi trading fees.

Kalshi's published general fee schedule: fee = round_up_to_cent(rate * C * P * (1 - P)),
taker rate 0.07, maker rate 0.0175 (where maker fees apply). Settlement is free.
Rates are configurable because Kalshi can change them per series — check the current fee schedule.
"""
from __future__ import annotations

import math


def kalshi_fee(contracts: int, price: float, rate: float) -> float:
    if contracts <= 0 or rate <= 0:
        return 0.0
    raw = rate * contracts * price * (1.0 - price)
    return math.ceil(round(raw * 100, 6)) / 100.0


def trade_economics(contracts: int, avg_price: float, fee: float, p_win: float) -> dict:
    """Dollar outcomes for buying `contracts` at `avg_price` with total `fee`."""
    cost = contracts * avg_price + fee
    payout = float(contracts)  # each winning contract pays $1
    profit_if_win = payout - cost
    loss_if_lose = cost
    ev = p_win * profit_if_win - (1 - p_win) * loss_if_lose
    return {
        "cost": round(cost, 4),
        "payout_if_win": round(payout, 4),
        "profit_if_win": round(profit_if_win, 4),
        "loss_if_lose": round(loss_if_lose, 4),
        "ev": round(ev, 4),
        "ev_per_dollar": round(ev / cost, 4) if cost > 0 else 0.0,
        "edge_per_contract": round(p_win - cost / contracts, 4) if contracts else 0.0,
        "breakeven_prob": round(cost / payout, 4) if payout else 1.0,
    }
