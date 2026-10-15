import numpy as np
import pandas as pd
import pytest

from propbot.synthetic import generate_mnq


@pytest.fixture(scope="module")
def bars():
    return generate_mnq(250, seed=7)


def test_shape_calendar_and_timezone(bars):
    assert len(bars) == 250 * 390
    assert str(bars.index.tz) == "America/New_York"
    assert bars.index.is_monotonic_increasing and bars.index.is_unique
    assert (bars.index.dayofweek < 5).all()
    hm = bars.index.strftime("%H:%M")
    assert hm.min() == "09:30" and hm.max() == "15:59"
    assert list(bars.columns) == ["open", "high", "low", "close", "volume"]


def test_bars_consistent_and_on_ticks(bars):
    px = bars[["open", "high", "low", "close"]].to_numpy()
    assert np.allclose(px / 0.25, np.round(px / 0.25))
    assert (bars.low <= bars[["open", "close"]].min(axis=1)).all()
    assert (bars.high >= bars[["open", "close"]].max(axis=1)).all()
    assert (bars.volume > 0).all()
    assert not bars.isna().any().any()


def test_deterministic_seed():
    a = generate_mnq(3, seed=11)
    b = generate_mnq(3, seed=11)
    c = generate_mnq(3, seed=12)
    pd.testing.assert_frame_equal(a, b)
    assert not a.equals(c)


def test_daily_volatility_realistic(bars):
    daily = bars.groupby(bars.index.date).agg(open=("open", "first"), close=("close", "last"),
                                              high=("high", "max"), low=("low", "min"))
    cc = np.log(daily.close).diff().dropna()
    assert 0.009 < cc.std() < 0.02
    gaps = np.log(daily.open / daily.close.shift()).dropna()
    assert (gaps.abs() > 0).mean() > 0.9
    rng = (daily.high - daily.low) / daily.open
    assert 0.008 < rng.median() < 0.035


def test_intraday_u_shape_and_fat_tails(bars):
    rng = (bars.high - bars.low)
    tod = bars.index.hour * 60 + bars.index.minute
    open_ = rng[tod < 600].mean()             # 09:30-10:00
    lunch = rng[(tod >= 720) & (tod < 810)].mean()
    close = rng[tod >= 930].mean()            # 15:30-16:00
    assert open_ > 1.5 * lunch and close > 1.2 * lunch
    r = np.log(bars.close).groupby(bars.index.date).diff().dropna()
    assert r.kurt() > 3


def test_null_mode_has_no_return_autocorrelation():
    b = generate_mnq(200, seed=3, regimes=False)
    r = np.log(b.close).groupby(b.index.date).diff().dropna()
    assert abs(r.autocorr(1)) < 0.03
    # 15-minute returns too (where regime drift would show up)
    r15 = np.log(b.close.iloc[14::15]).groupby(b.index[14::15].date).diff().dropna()
    assert abs(r15.autocorr(1)) < 0.06


def test_freq_resampling():
    b = generate_mnq(2, seed=1, freq="5min")
    assert len(b) == 2 * 78
    assert (b.index.minute % 5 == 0).all()
    with pytest.raises(ValueError):
        generate_mnq(2, seed=1, freq="30s")
