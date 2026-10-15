"""Intraday futures strategies built for prop-firm evaluation rules.

``REGISTRY`` maps strategy name -> (class, param_grid). ``param_grid`` is a dict of lists for
grid search; parameters not in the grid take the class defaults (``cls.default_params``).
"""
from __future__ import annotations

import itertools
from typing import Dict, Iterator, Tuple, Type

from .base import BaseStrategy
from . import ema_trend, opening_drive, orb, prior_day_levels, vwap_pullback, vwap_reversion
from .ema_trend import EMATrend
from .opening_drive import OpeningDrive
from .orb import OpeningRangeBreakout
from .prior_day_levels import PriorDayLevels
from .vwap_pullback import VWAPPullback
from .vwap_reversion import VWAPReversion

REGISTRY: Dict[str, Tuple[Type[BaseStrategy], dict]] = {
    OpeningRangeBreakout.name: (OpeningRangeBreakout, orb.PARAM_GRID),
    VWAPPullback.name: (VWAPPullback, vwap_pullback.PARAM_GRID),
    VWAPReversion.name: (VWAPReversion, vwap_reversion.PARAM_GRID),
    OpeningDrive.name: (OpeningDrive, opening_drive.PARAM_GRID),
    PriorDayLevels.name: (PriorDayLevels, prior_day_levels.PARAM_GRID),
    EMATrend.name: (EMATrend, ema_trend.PARAM_GRID),
}


def iter_grid(grid: dict) -> Iterator[dict]:
    """Yield every parameter combination of a dict-of-lists grid."""
    keys = list(grid)
    for vals in itertools.product(*(grid[k] for k in keys)):
        yield dict(zip(keys, vals))


def make(name: str, **params) -> BaseStrategy:
    """Instantiate a registered strategy by name."""
    cls, _ = REGISTRY[name]
    return cls(**params)


__all__ = [
    "REGISTRY", "iter_grid", "make", "BaseStrategy",
    "OpeningRangeBreakout", "VWAPPullback", "VWAPReversion", "OpeningDrive",
    "PriorDayLevels", "EMATrend",
]
