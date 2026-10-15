"""Shared contracts between propbot modules. Every module codes against these.

Bars: a pandas DataFrame indexed by tz-aware America/New_York timestamps (bar OPEN time),
columns: open, high, low, close, volume (floats). Regular trading hours 09:30-16:00 ET
unless a module says otherwise. One "session" = one calendar trading date.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol

import pandas as pd


@dataclass(frozen=True)
class ContractSpec:
    symbol: str
    point_value: float      # $ per 1.0 index point per contract
    tick_size: float
    commission_rt: float    # round-turn commission + fees per contract, $
    mini_equivalent: float  # 1 mini = 1.0, 1 micro = 0.1 (for the max-size rule)


CONTRACTS = {
    "MNQ": ContractSpec("MNQ", 2.0, 0.25, 1.04, 0.1),
    "NQ": ContractSpec("NQ", 20.0, 0.25, 4.0, 1.0),
    "MES": ContractSpec("MES", 5.0, 0.25, 1.04, 0.1),
    "ES": ContractSpec("ES", 50.0, 0.25, 4.0, 1.0),
}


@dataclass(frozen=True)
class EvalRules:
    """Lucid Trading 25K Daily Eval, EOD drawdown variant (from the user's screenshot)."""
    start_balance: float = 25_000.0
    profit_target: float = 1_250.0
    max_loss: float = 1_000.0            # EOD trailing: floor = max(EOD balance high) - max_loss
    trailing_lock_at: Optional[float] = None  # floor stops trailing once it reaches this balance (None = never)
    daily_loss_limit: Optional[float] = 600.0  # None = OFF
    consistency: float = 0.50            # largest single-day profit must be <= this * total profit at pass time
    max_minis: float = 2.0               # 2 minis or 20 micros
    min_days: int = 2                    # "2-day pass"
    flatten_time: str = "15:55"          # ET; bot must be flat by this time
    eval_fee: float = 55.30
    reset_fee: float = 55.00


@dataclass
class Signal:
    """Emitted by a strategy on bar close; the backtester fills at next bar open (+slippage)."""
    side: int                     # +1 long, -1 short, 0 = flatten
    stop: Optional[float] = None  # absolute price
    target: Optional[float] = None
    tag: str = ""


class Strategy(Protocol):
    name: str
    params: dict

    def reset(self) -> None:
        """Called at the start of every session."""

    def on_bar(self, i: int, bars: pd.DataFrame, position: int) -> Optional[Signal]:
        """bars = the current session's bars up to and including index i (no lookahead).
        position = current signed contract count. Return a Signal or None."""


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: int
    qty: int
    entry: float
    exit: float
    pnl: float          # net $ after commissions/slippage
    reason: str = ""


@dataclass
class DayResult:
    date: pd.Timestamp
    pnl: float
    trades: list = field(default_factory=list)
    max_intraday_drawdown: float = 0.0   # worst open+closed P&L dip during the day, $ (<= 0)
