"""Structured (JSON-lines) decision log shared by every live agent."""
from __future__ import annotations

import json
import logging
import math
import os
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
import pandas as pd

__all__ = ["EventLog"]

_LEVELS = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
           "error": logging.ERROR, "critical": logging.CRITICAL}


def _jsonable(x: Any) -> Any:
    if isinstance(x, (pd.Timestamp, datetime)):
        return x.isoformat()
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        f = float(x)
        return f if math.isfinite(f) else str(f)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    return x


class EventLog:
    """Appends one JSON object per event to ``path`` (if given) and mirrors it to the
    ``propbot.live`` python logger. Every record has ``wall`` (UTC wall clock), ``ts``
    (market time of the bar being processed, if any), ``agent``, ``event`` and free fields.

    ``events`` keeps the records in memory (tests / CLI summaries)."""

    def __init__(self, path: Optional[str] = None, logger_name: str = "propbot.live",
                 keep: bool = True):
        self.path = path
        self.keep = keep
        self.events: list[dict] = []
        self._fh = None
        self.logger = logging.getLogger(logger_name)
        if path:
            d = os.path.dirname(os.path.abspath(path))
            os.makedirs(d, exist_ok=True)
            self._fh = open(path, "a", encoding="utf-8")

    def emit(self, agent: str, event: str, ts: Any = None, level: str = "info",
             **fields: Any) -> dict:
        rec = {"wall": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
               "ts": _jsonable(ts) if ts is not None else None,
               "level": level, "agent": agent, "event": event}
        rec.update(_jsonable(fields))
        if self.keep:
            self.events.append(rec)
        if self._fh is not None:
            self._fh.write(json.dumps(rec, default=str) + "\n")
            self._fh.flush()
        lvl = _LEVELS.get(level, logging.INFO)
        if self.logger.isEnabledFor(lvl):
            msg = fields.get("reason") or fields.get("msg") or ""
            self.logger.log(lvl, "[%s] %s %s %s", agent, event, rec["ts"] or "", msg)
        return rec

    def find(self, event: Optional[str] = None, agent: Optional[str] = None) -> list[dict]:
        return [e for e in self.events
                if (event is None or e["event"] == event) and (agent is None or e["agent"] == agent)]

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None
