"""Loading, cleaning and slicing intraday futures bars.

Every function here returns / accepts the ``Bars`` format defined in
:mod:`propbot.interfaces`: a DataFrame indexed by tz-aware America/New_York
timestamps of the bar OPEN time, with float columns open, high, low, close, volume.

Getting data
------------
Yahoo/Stooq do not carry usable intraday futures history, so export from your
platform or buy it. 1-minute bars are the recommended research resolution.

NinjaTrader 8 (free with a Kinetick/CQG/Rithmic data connection)
    Control Center -> Tools -> Historical Data -> "Load" the instrument (e.g.
    ``MNQ 12-26`` or the ``MNQ ##-##`` continuous/merged contract) for the date
    range, then the "Export" section: Data type ``Last``, Period ``Minute``,
    choose the instrument and dates, Export. The file is ``.txt`` with lines like
    ``20240102 093100;16850.25;16852.5;16848;16851.75;812``. NinjaTrader stamps
    each bar with its CLOSE time in the time zone configured under Tools ->
    Options -> General (usually your PC's local zone); pass ``src_tz=`` if that
    is not America/New_York. ``load_csv`` shifts the stamp back to the bar open.

Tradovate / TradingView
    TradingView chart (Tradovate-connected or CME data) -> the arrow next to the
    layout name -> "Export chart data..." -> time format ISO or UNIX. The CSV has
    a header ``time,open,high,low,close,Volume``; times are bar OPEN times.
    Any similar CSV with a header works: a ``time``/``datetime``/``timestamp``
    column, or separate ``date`` and ``time`` columns, plus open/high/low/close
    (``last`` is accepted for close) and an optional volume column, matched
    case-insensitively. Naive timestamps are interpreted in ``src_tz``.

Databento (pay-as-you-go, best quality; free credits for new accounts)
    Dataset ``GLBX.MDP3``, schema ``ohlcv-1m``, symbols e.g. ``MNQ.c.0``
    (continuous front month, stype ``continuous``) or ``MNQ.FUT`` (parent; we
    pick the highest-volume outright per day), encoding CSV. Either the default
    fixed-point prices (integers scaled by 1e9) and nanosecond ``ts_event``, or
    ``pretty_px``/``pretty_ts``, are detected automatically. ``ts_event`` is
    the bar open in UTC.

After loading, use :func:`rth` to keep regular trading hours, :func:`resample`
for higher timeframes and :func:`sessions` to iterate trading days.
"""
from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Iterator, Optional, Union

import numpy as np
import pandas as pd

__all__ = ["load_csv", "rth", "resample", "sessions", "clean"]

OHLCV = ["open", "high", "low", "close", "volume"]
_NT8_LINE = re.compile(r"^\s*\d{8}\s+\d{6}\s*;")
_FIXED_POINT_THRESHOLD = 1e7  # no futures we care about trades above 10 million points
_UNDEF_PRICE = np.iinfo(np.int64).max

PathLike = Union[str, Path]


# --------------------------------------------------------------------------- loading
def load_csv(
    path: PathLike,
    fmt: str = "auto",
    tz: str = "America/New_York",
    *,
    src_tz: Optional[str] = None,
    symbol: Optional[str] = None,
    bar_label: str = "auto",
) -> pd.DataFrame:
    """Load a bar file into the ``Bars`` format.

    Parameters
    ----------
    path : file path (or a file-like object).
    fmt : ``"auto"`` (default), ``"ninjatrader"``, ``"generic"`` (Tradovate /
        TradingView / any headered CSV) or ``"databento"``.
    tz : output time zone (the toolkit assumes America/New_York).
    src_tz : time zone of NAIVE timestamps in the file. Defaults to ``tz``.
        Tz-aware strings, unix epochs and Databento timestamps ignore it.
    symbol : Databento only - keep just this symbol / instrument_id. If omitted
        and the file holds several outright contracts, the highest-volume one is
        kept for each trading date (simple front-month roll); spreads are dropped.
    bar_label : ``"open"``, ``"close"`` or ``"auto"``. Whether the file stamps bars
        with their open or close time. Auto = close for NinjaTrader, open otherwise.

    Returns a sorted, de-duplicated, NaN-free Bars DataFrame (all sessions, not
    just RTH - call :func:`rth` afterwards).
    """
    src_tz = src_tz or tz
    raw = _read_text(path)
    if fmt == "auto":
        fmt = _detect_format(raw)
    fmt = {"nt8": "ninjatrader", "tradovate": "generic", "tradingview": "generic"}.get(fmt, fmt)

    if fmt == "ninjatrader":
        df = _parse_ninjatrader(raw, src_tz)
        label = "close" if bar_label == "auto" else bar_label
    elif fmt == "databento":
        df = _parse_databento(raw, tz, symbol)
        label = "open" if bar_label == "auto" else bar_label
    elif fmt == "generic":
        df = _parse_generic(raw, src_tz)
        label = "open" if bar_label == "auto" else bar_label
    else:
        raise ValueError(f"unknown fmt {fmt!r}")

    df.index = df.index.tz_convert(tz)
    df = clean(df)
    if label == "close":
        df.index = df.index - infer_bar_duration(df.index)
    elif label != "open":
        raise ValueError("bar_label must be 'open', 'close' or 'auto'")
    df.index.name = "time"
    return df


def _read_text(path) -> str:
    if hasattr(path, "read"):
        data = path.read()
        return data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return Path(path).read_text(encoding="utf-8-sig")


def _detect_format(raw: str) -> str:
    first = next((ln for ln in raw.splitlines() if ln.strip()), "")
    if _NT8_LINE.match(first):
        return "ninjatrader"
    header = [c.strip().strip('"').lower() for c in re.split(r"[,;\t]", first)]
    if "ts_event" in header:
        return "databento"
    return "generic"


def _parse_ninjatrader(raw: str, src_tz: str) -> pd.DataFrame:
    df = pd.read_csv(
        io.StringIO(raw), sep=";", header=None, names=["ts"] + OHLCV, dtype={"ts": str}
    )
    ts = pd.to_datetime(df["ts"].str.strip(), format="%Y%m%d %H%M%S")
    idx = pd.DatetimeIndex(ts).tz_localize(src_tz, ambiguous="infer", nonexistent="shift_forward")
    out = df[OHLCV].set_axis(idx)
    return out


def _sniff_sep(raw: str) -> str:
    first = next((ln for ln in raw.splitlines() if ln.strip()), "")
    counts = {s: first.count(s) for s in [",", ";", "\t"]}
    return max(counts, key=counts.get)


def _to_index(values: pd.Series, src_tz: str) -> pd.DatetimeIndex:
    """Parse a timestamp column that may be epoch numbers, aware or naive strings."""
    if pd.api.types.is_numeric_dtype(values):
        v = values.astype("float64")
        mag = np.nanmedian(np.abs(v.to_numpy()))
        unit = "ns" if mag > 1e17 else "us" if mag > 1e14 else "ms" if mag > 1e11 else "s"
        return pd.DatetimeIndex(pd.to_datetime(values.astype("int64"), unit=unit, utc=True))
    s = values.astype(str).str.strip()
    if s.str.fullmatch(r"\d{9,19}").all():
        return _to_index(s.astype("int64"), src_tz)
    sample = s.iloc[0] if len(s) else ""
    aware = bool(re.search(r"(Z|[+-]\d{2}:?\d{2})$", sample))
    if aware:
        return pd.DatetimeIndex(pd.to_datetime(s, utc=True, format="mixed"))
    idx = pd.DatetimeIndex(pd.to_datetime(s, format="mixed"))
    return idx.tz_localize(src_tz, ambiguous="infer", nonexistent="shift_forward")


def _parse_generic(raw: str, src_tz: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(raw), sep=_sniff_sep(raw))
    df.columns = [str(c).strip().strip('"').lower() for c in df.columns]
    rename = {"last": "close", "vol": "volume", "volume_total": "volume", "o": "open",
              "h": "high", "l": "low", "c": "close", "v": "volume"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns and v not in df.columns})
    missing = [c for c in ["open", "high", "low", "close"] if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing price columns {missing}; columns = {list(df.columns)}")

    if "date" in df.columns and "time" in df.columns:
        stamp = df["date"].astype(str).str.strip() + " " + df["time"].astype(str).str.strip()
    else:
        for name in ("datetime", "timestamp", "time", "date", "ts", "date_time", "ts_event"):
            if name in df.columns:
                stamp = df[name]
                break
        else:
            raise ValueError(f"no timestamp column found; columns = {list(df.columns)}")
    idx = _to_index(stamp, src_tz)
    if "volume" not in df.columns:
        df["volume"] = 0.0
    out = df[OHLCV].set_axis(idx)
    return out


def _parse_databento(raw: str, tz: str, symbol: Optional[str]) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(raw), sep=_sniff_sep(raw))
    df.columns = [str(c).strip().lower() for c in df.columns]
    df.index = _to_index(df["ts_event"], "UTC")
    for col in ["open", "high", "low", "close"]:
        v = pd.to_numeric(df[col], errors="coerce").astype("float64")
        df[col] = v.mask(v >= float(_UNDEF_PRICE))
    if np.nanmedian(df["close"].to_numpy()) > _FIXED_POINT_THRESHOLD:
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]] / 1e9
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").astype("float64")
    else:
        df["volume"] = 0.0

    key = "symbol" if "symbol" in df.columns else "instrument_id" if "instrument_id" in df.columns else None
    if key is not None:
        df[key] = df[key].astype(str)
        if symbol is not None:
            df = df[df[key] == str(symbol)]
            if df.empty:
                raise ValueError(f"symbol {symbol!r} not found in file")
        elif df[key].nunique() > 1:
            if key == "symbol":
                df = df[~df[key].str.contains("-", regex=False)]  # drop calendar spreads
            day = df.index.tz_convert(tz).normalize()
            vol = df.groupby([day, df[key]])["volume"].sum()
            best = vol.groupby(level=0).idxmax().map(lambda t: t[1])
            df = df[df[key].to_numpy() == best.reindex(day).to_numpy()]
    return df[OHLCV].copy()


# --------------------------------------------------------------------------- cleaning
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Sort, de-duplicate (last wins), drop NaN prices, coerce to float and repair
    bars whose high/low do not bracket open/close."""
    df = df[OHLCV].apply(pd.to_numeric, errors="coerce").astype("float64")
    df["volume"] = df["volume"].fillna(0.0)
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[~df.index.isna()]
    df = df.sort_index(kind="stable")
    df = df[~df.index.duplicated(keep="last")]
    px = df[["open", "high", "low", "close"]].to_numpy()
    df["high"] = px.max(axis=1)
    df["low"] = px.min(axis=1)
    return df


def infer_bar_duration(index: pd.DatetimeIndex) -> pd.Timedelta:
    """Most common positive spacing between consecutive bars (the bar size)."""
    if len(index) < 2:
        return pd.Timedelta(minutes=1)
    d = np.diff(index.asi8)
    d = d[d > 0]
    if d.size == 0:
        return pd.Timedelta(minutes=1)
    vals, counts = np.unique(d, return_counts=True)
    unit = index.unit if hasattr(index, "unit") else "ns"
    return pd.Timedelta(int(vals[np.argmax(counts)]), unit=unit)


# --------------------------------------------------------------------------- slicing
def rth(bars: pd.DataFrame, start: str = "09:30", end: str = "16:00") -> pd.DataFrame:
    """Keep bars whose OPEN time is in [start, end) local time. Weekend bars are dropped."""
    out = bars.between_time(start, end, inclusive="left")
    return out[out.index.dayofweek < 5]


def resample(bars: pd.DataFrame, rule: str, offset: Optional[str] = None) -> pd.DataFrame:
    """Aggregate to a higher timeframe (e.g. ``"5min"``) without crossing sessions.

    Bins are left-labelled/left-closed (bar open time), anchored at midnight of
    each day (plus ``offset``), so 5/15/30-minute bins line up with 09:30. Empty
    bins are dropped.
    """
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    out = bars.resample(rule, label="left", closed="left", origin="start_day", offset=offset).agg(agg)
    return out.dropna(subset=["open", "high", "low", "close"])


def sessions(bars: pd.DataFrame) -> Iterator[tuple[pd.Timestamp, pd.DataFrame]]:
    """Yield ``(date, session_df)`` per calendar trading date (local time).

    ``date`` is a tz-naive midnight Timestamp. Assumes ``bars`` is sorted (as
    returned by :func:`load_csv` / :func:`rth`). For RTH bars one date is one session.
    """
    if bars.empty:
        return
    days = bars.index.normalize().tz_localize(None)
    codes = days.asi8
    cuts = np.flatnonzero(np.diff(codes)) + 1
    starts = np.concatenate([[0], cuts])
    ends = np.concatenate([cuts, [len(bars)]])
    for s, e in zip(starts, ends):
        yield days[s], bars.iloc[s:e]
