import math

import pandas as pd
import pytest

from propbot.interfaces import DayResult, EvalRules
from propbot.rules import (ACTIVE, FAILED, PASSED, EvalAccount, EvalOptions, room_today,
                           simulate_eval)

NO_DLL = EvalRules(daily_loss_limit=None)


def D(pnl, low=None, trades=True, i=0):
    """DayResult helper; low defaults to min(pnl, 0)."""
    return DayResult(date=pd.Timestamp("2024-01-02") + pd.Timedelta(days=i), pnl=float(pnl),
                     trades=["t"] if trades else [],
                     max_intraday_drawdown=float(min(pnl, 0) if low is None else low))


def test_initial_state():
    a = EvalAccount()
    assert a.balance == 25_000 and a.floor == 24_000 and a.eod_high == 25_000
    assert a.status == ACTIVE and a.days_traded == 0 and a.best_day == 0


def test_floor_trails_only_at_eod_and_never_falls():
    a = EvalAccount(NO_DLL)
    # +500 close; intraday dip -200 never matters to the floor, only the EOD balance does
    assert a.apply_day(D(500, low=-200)) == ACTIVE
    assert a.floor == 24_500 and a.eod_high == 25_500
    # dip to 25,500 - 900 = 24,600 (> floor 24,500) is survivable; closes -800
    assert a.apply_day(D(-800, low=-900)) == ACTIVE
    assert a.balance == 24_700 and a.floor == 24_500        # floor did not drop
    assert a.apply_day(D(300)) == ACTIVE
    assert a.balance == 25_000 and a.floor == 24_500 and a.eod_high == 25_500


def test_intraday_breach_via_max_intraday_drawdown():
    a = EvalAccount(NO_DLL)
    # closes green but open P&L touched -1000 -> 24,000 = floor -> fail (touch counts)
    assert a.apply_day(D(100, low=-1000)) == FAILED
    assert a.fail_reason == "max_loss" and a.balance == 24_000
    b = EvalAccount(NO_DLL)
    assert b.apply_day(D(100, low=-999.99)) == ACTIVE
    assert b.balance == 25_100


def test_intraday_breach_after_trail():
    a = EvalAccount(NO_DLL)
    a.apply_day(D(800))                       # floor -> 24,800
    assert a.floor == 24_800
    assert a.apply_day(D(-50, low=-1000)) == FAILED   # 25,800 - 1000 touches 24,800
    assert a.fail_reason == "max_loss"


def test_breach_and_dll_floor_takes_precedence():
    a = EvalAccount()                         # default DLL 600, as-is (backtester) mode
    a.apply_day(D(800))
    assert a.apply_day(D(-50, low=-1000)) == FAILED
    assert a.fail_reason == "max_loss"


def test_dll_flatten_at_limit_protects_floor():
    # firm liquidates at -600, so a -1000 low in the raw data never reaches the floor
    a = EvalAccount(dll_flatten_at_limit=True)
    a.apply_day(D(800))
    assert a.apply_day(D(200, low=-1000)) == ACTIVE
    assert a.balance == 25_800 - 600
    assert a.history[-1]["dll_hit"] and a.history[-1]["pnl_effective"] == -600
    # but when room to floor < DLL the floor still breaches first
    b = EvalAccount(dll_flatten_at_limit=True)
    b.apply_day(D(-500, low=-500))            # 24,500, floor 24,000 -> room 500 < 600
    assert b.apply_day(D(0, low=-650)) == FAILED and b.fail_reason == "max_loss"


def test_soft_dll_does_not_fail_and_records_realised_pnl():
    a = EvalAccount()
    assert a.apply_day(D(-620, low=-650)) == ACTIVE      # backtester stopped the day
    assert a.balance == 25_000 - 620
    assert a.history[-1]["dll_hit"] is True


def test_hard_dll_fails():
    a = EvalAccount(dll_is_hard_breach=True)
    assert a.apply_day(D(-620, low=-650)) == FAILED
    assert a.fail_reason == "daily_loss_limit"
    b = EvalAccount(dll_is_hard_breach=True)
    assert b.apply_day(D(-590, low=-599)) == ACTIVE


def test_pass_requires_min_two_traded_days():
    a = EvalAccount(consistency_mode="ignore")
    assert a.apply_day(D(1300)) == ACTIVE                 # target hit on day 1, 1 traded day
    assert a.apply_day(D(0, trades=False)) == ACTIVE      # untraded day does not count
    assert a.days_used == 2 and a.days_traded == 1
    assert a.apply_day(D(10)) == PASSED
    assert a.days_used == 3 and a.days_traded == 2 and a.reason == "passed"


def test_pass_exactly_at_consistency_boundary():
    out = simulate_eval([D(625), D(625)])
    assert out.passed and out.days_used == 2 and out.reason == "passed"
    assert out.final_balance == 26_250


def test_consistency_extension():
    a = EvalAccount()
    a.apply_day(D(700))
    assert a.apply_day(D(600)) == ACTIVE        # 1300 >= 1250 but 700 > 650
    assert a.consistency_extended and a.effective_target == 1400
    assert a.apply_day(D(50)) == ACTIVE         # 1350: 700 > 675
    assert a.apply_day(D(60)) == PASSED         # 1410: 700 <= 705
    assert a.reason == "passed_after_consistency_extension"


def test_consistency_fail_mode_and_ignore_mode():
    out = simulate_eval([D(700), D(600)], consistency_mode="fail")
    assert out.failed and out.reason == "consistency" and out.days_used == 2
    out = simulate_eval([D(700), D(600)], consistency_mode="ignore")
    assert out.passed and out.days_used == 2


def test_consistency_uses_net_total_profit():
    # a losing day lowers total profit, so later big days become inconsistent
    a = EvalAccount(NO_DLL)
    for d in (D(-500), D(875), D(875)):
        a.apply_day(d)
    assert a.profit == 1250 and a.status == ACTIVE      # 875 > 625
    assert a.effective_target == 1750


def test_trailing_lock():
    r = EvalRules(profit_target=5_000, trailing_lock_at=25_100, daily_loss_limit=None)
    a = EvalAccount(r)
    a.apply_day(D(800))
    assert a.floor == 24_800
    a.apply_day(D(700))
    assert a.floor == 25_100
    a.apply_day(D(1000))
    assert a.floor == 25_100


def test_simulate_eval_timeout_and_max_days():
    out = simulate_eval([D(10)] * 5)
    assert not out.passed and not out.failed and out.reason == "timeout" and out.timed_out
    assert out.days_used == 5
    out = simulate_eval([D(400)] * 10, max_days=3)
    assert out.reason == "timeout" and out.days_used == 3
    out = simulate_eval([D(400)] * 10)
    assert out.passed and out.days_used == 4         # 1600 on day 4, best 400


def test_simulate_eval_stops_after_fail():
    out = simulate_eval([D(-300)] * 10)
    # 24,700 / 24,400 / 24,100 / 23,800 -> fails on day 4
    assert out.failed and out.days_used == 4 and out.reason == "max_loss"
    assert out.final_balance == 24_000


def test_apply_day_after_terminal_is_noop():
    a = EvalAccount(NO_DLL)
    a.apply_day(D(-1000))
    assert a.status == FAILED
    assert a.apply_day(D(5000)) == FAILED and a.days_used == 1


def test_positive_drawdown_rejected():
    with pytest.raises(ValueError):
        EvalAccount().apply_day(D(100, low=50))


def test_options_validation():
    with pytest.raises(ValueError):
        EvalOptions(consistency_mode="bogus")


# ------------------------------------------------------------------------ room_today
def test_room_today_fresh_account():
    room = room_today(EvalAccount())
    assert room["max_loss_today"] == 600            # min(1000, DLL 600)
    assert room["profit_needed"] == 1250
    assert room["max_profit_today_for_consistency"] == 625
    assert room["can_pass_today"] is False           # needs 1250 > 625 cap, and 2 days


def test_room_today_after_days():
    a = EvalAccount()
    a.apply_day(D(500))
    room = room_today(a)
    assert room["profit_needed"] == 750 and room["max_profit_today_for_consistency"] == 625
    assert room["max_loss_today"] == 600
    assert room["can_pass_today"] is False
    a.apply_day(D(600))                              # profit 1100, best 600
    room = room_today(a)
    assert room["profit_needed"] == 150
    assert room["max_profit_today_for_consistency"] == 1100   # c*P/(1-c) = P
    assert room["can_pass_today"] is True
    # banking exactly the cap passes today
    assert a.apply_day(D(1100)) == PASSED


def test_room_today_big_first_day_raises_target():
    a = EvalAccount(NO_DLL)
    a.apply_day(D(900))
    room = room_today(a)
    assert room["effective_target"] == 1800
    assert room["profit_needed"] == 900
    assert room["max_profit_today_for_consistency"] == 900
    assert a.apply_day(D(900)) == PASSED


def test_room_today_near_floor_and_buffer():
    a = EvalAccount()
    a.apply_day(D(-590))                              # 24,410 vs floor 24,000
    room = room_today(a)
    assert room["max_loss_today"] == pytest.approx(410)
    assert room_today(a, safety_buffer=50)["max_loss_today"] == pytest.approx(360)
    # after a loss the consistency cap stays at c * target (recover with more days)
    assert room["max_profit_today_for_consistency"] == 625
    assert room["profit_needed"] == pytest.approx(1840)


def test_room_today_consistency_off_and_terminal():
    a = EvalAccount(consistency_mode="ignore")
    assert math.isinf(room_today(a)["max_profit_today_for_consistency"])
    b = EvalAccount(NO_DLL)
    b.apply_day(D(-1000))
    assert room_today(b)["max_loss_today"] == 0 and room_today(b)["status"] == FAILED
