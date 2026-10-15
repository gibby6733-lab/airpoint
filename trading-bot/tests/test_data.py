import io

import numpy as np
import pandas as pd
import pytest

from propbot.data import load_csv, resample, rth, sessions

NY = "America/New_York"


def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text)
    return p


def test_ninjatrader_close_stamps_shifted_to_open(tmp_path):
    text = (
        "20240102 093200;101;102;100.5;101.5;20\n"
        "20240102 093100;100;101.25;99.75;101;10\n"   # out of order
        "20240102 093300;101.5;103;101;102.75;30\n"
        "20240102 093300;101.5;103;101;102.75;30\n"   # duplicate
    )
    df = load_csv(write(tmp_path, "MNQ.Last.txt", text))
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert str(df.index.tz) == NY
    assert list(df.index) == list(pd.date_range("2024-01-02 09:30", periods=3, freq="1min", tz=NY))
    assert df.iloc[0].tolist() == [100, 101.25, 99.75, 101, 10]
    assert df.dtypes.eq("float64").all()


def test_ninjatrader_source_timezone(tmp_path):
    text = "20240102 083100;1;2;0.5;1.5;1\n20240102 083200;1;2;0.5;1.5;1\n"
    df = load_csv(write(tmp_path, "nt.txt", text), src_tz="America/Chicago")
    assert df.index[0] == pd.Timestamp("2024-01-02 09:30", tz=NY)


def test_generic_date_time_columns_case_insensitive(tmp_path):
    text = (
        "Date,Time,Open,High,Low,Last,Volume\n"
        "01/02/2024,09:30:00,100,101,99,100.5,5\n"
        "01/02/2024,09:31:00,100.5,102,100,101.5,6\n"
        "01/02/2024,09:32:00,,102,100,101.5,6\n"      # NaN open -> dropped
    )
    df = load_csv(write(tmp_path, "tradovate.csv", text))
    assert len(df) == 2
    assert df.index[0] == pd.Timestamp("2024-01-02 09:30", tz=NY)
    assert df["close"].tolist() == [100.5, 101.5]


def test_tradingview_unix_and_iso(tmp_path):
    t0 = int(pd.Timestamp("2024-07-01 09:30", tz=NY).timestamp())
    text = f"time,open,high,low,close,Volume\n{t0},1,2,0.5,1.5,7\n{t0 + 60},1.5,2,1,1.75,8\n"
    df = load_csv(write(tmp_path, "tv.csv", text))
    assert df.index[0] == pd.Timestamp("2024-07-01 09:30", tz=NY)
    assert df["volume"].tolist() == [7, 8]

    text = "time,open,high,low,close\n2024-07-01T09:30:00-04:00,1,2,0.5,1.5\n2024-07-01T09:31:00-04:00,1,2,0.5,1.5\n"
    df = load_csv(write(tmp_path, "tv_iso.csv", text))
    assert df.index[1] == pd.Timestamp("2024-07-01 09:31", tz=NY)
    assert (df["volume"] == 0).all()


def test_databento_fixed_point_and_front_month(tmp_path):
    t = pd.Timestamp("2024-03-01 14:30", tz="UTC")  # 09:30 ET
    ns = [t.value, t.value + 60_000_000_000]
    rows = ["ts_event,rtype,publisher_id,instrument_id,open,high,low,close,volume,symbol"]
    for k, ts in enumerate(ns):
        p = int((18000 + k) * 1e9)
        rows.append(f"{ts},33,1,111,{p},{p + 500_000_000},{p - 250_000_000},{p},1000,MNQH4")
        rows.append(f"{ts},33,1,222,{p + 100 * 10**9},{p + 101 * 10**9},{p + 99 * 10**9},{p + 100 * 10**9},10,MNQM4")
        rows.append(f"{ts},33,1,333,{int(100e9)},{int(101e9)},{int(99e9)},{int(100e9)},5000,MNQH4-MNQM4")
    df = load_csv(write(tmp_path, "glbx-mdp3.ohlcv-1m.csv", "\n".join(rows) + "\n"))
    assert len(df) == 2
    assert df.index[0] == pd.Timestamp("2024-03-01 09:30", tz=NY)
    assert df["open"].tolist() == [18000.0, 18001.0]
    assert df["high"].iloc[0] == 18000.5

    df2 = load_csv(write(tmp_path, "db2.csv", "\n".join(rows) + "\n"), symbol="MNQM4")
    assert df2["open"].iloc[0] == 18100.0


def test_databento_pretty(tmp_path):
    text = (
        "ts_event,rtype,publisher_id,instrument_id,open,high,low,close,volume,symbol\n"
        "2024-03-01T14:30:00.000000000Z,33,1,111,18000.25,18001.0,17999.5,18000.75,12,MNQH4\n"
    )
    df = load_csv(io.StringIO(text))
    assert df.index[0] == pd.Timestamp("2024-03-01 09:30", tz=NY)
    assert df["close"].iloc[0] == 18000.75


def test_explicit_fmt_and_high_low_repair(tmp_path):
    text = "time,open,high,low,close,volume\n2024-01-02 09:30,100,99,101,100,1\n"  # high/low swapped
    df = load_csv(write(tmp_path, "x.csv", text), fmt="generic")
    assert df["high"].iloc[0] == 101 and df["low"].iloc[0] == 99
    with pytest.raises(ValueError):
        load_csv(write(tmp_path, "y.csv", text), fmt="nope")


def _minute_bars(start, end):
    idx = pd.date_range(start, end, freq="1min", tz=NY, inclusive="left")
    x = np.arange(len(idx), dtype=float)
    return pd.DataFrame({"open": x, "high": x + 1, "low": x - 1, "close": x + 0.5, "volume": 1.0}, index=idx)


def test_rth_resample_sessions():
    bars = pd.concat([
        _minute_bars("2024-01-02 08:00", "2024-01-02 17:00"),
        _minute_bars("2024-01-03 08:00", "2024-01-03 17:00"),
        _minute_bars("2024-01-06 09:30", "2024-01-06 10:00"),  # Saturday
    ])
    r = rth(bars)
    assert len(r) == 2 * 390
    assert r.index[0].strftime("%H:%M") == "09:30" and r.index[389].strftime("%H:%M") == "15:59"

    r5 = resample(r, "5min")
    assert len(r5) == 2 * 78
    first = r.iloc[:5]
    assert r5.iloc[0].tolist() == [first.open.iloc[0], first.high.max(), first.low.min(), first.close.iloc[-1], 5.0]
    assert r5.index[0] == pd.Timestamp("2024-01-02 09:30", tz=NY)

    days = list(sessions(r))
    assert [d for d, _ in days] == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
    assert all(len(s) == 390 for _, s in days)
    assert list(sessions(r.iloc[:0])) == []
