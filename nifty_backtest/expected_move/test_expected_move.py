"""Tests for analyze.py. Run: python -m pytest -q expected_move"""
import datetime as dt
import importlib.util
import math
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location("em_analyze", Path(__file__).with_name("analyze.py"))
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
D = dt.date


@pytest.fixture(scope="module")
def cal():
    h = an.load_history()
    return an.expiry_calendars(list(h["date"]), h["date"].max())


def test_holiday_shifts_thursday_era(cal):
    weekly, monthly = cal
    assert D(2019, 2, 14) in weekly                       # first NIFTY weekly expiry
    assert D(2021, 11, 3) in weekly and D(2021, 11, 4) not in weekly   # Diwali Thursday -> Wednesday
    assert D(2023, 1, 25) in weekly                       # Republic Day Thursday -> Wednesday
    assert D(2023, 3, 29) in monthly                      # Ram Navami Thursday -> Wednesday (monthly)
    assert D(2024, 8, 14) in weekly                       # Independence Day Thursday -> Wednesday


def test_tuesday_era(cal):
    weekly, monthly = cal
    assert D(2025, 8, 28) in weekly and D(2025, 9, 2) in weekly    # last Thursday, first Tuesday expiry
    assert D(2025, 9, 30) in monthly                      # first last-Tuesday monthly expiry
    assert D(2026, 10, 19) in weekly                      # Dussehra Tuesday -> Monday
    assert D(2026, 11, 9) in weekly                       # Diwali Balipratipada Tuesday -> Monday


def test_formulas_match_reels():
    assert 23900 * 0.1068 * math.sqrt(2 / 365) == pytest.approx(188.95, abs=0.01)          # reel 1
    k = 0.19 * math.sqrt(5 / 365)
    s = 24500 / math.exp(an.N.inv_cdf(0.93) * k)
    assert an.N.cdf(math.log(24500 / s) / k) == pytest.approx(0.93)                          # reel 2
    assert 1 - an.N.cdf(math.log(22800 / s) / k) == pytest.approx(0.961, abs=0.001)


def test_observation_example():
    h = an.load_history()
    weekly, _ = an.expiry_calendars(list(h["date"]), h["date"].max())
    o = an.observations(h, weekly, "weekly", an.WEEKLY_LAUNCH).set_index("origin")
    r = o.loc[D(2026, 9, 4)]
    assert r["expiry"] == D(2026, 9, 8) and r["dte"] == 4
    assert r["expected_move"] == pytest.approx(23897.70 * 0.1068 * math.sqrt(4 / 365))
    assert bool(r["close_inside"]) and not bool(r["range_inside"])   # closed inside, but low broke the band
