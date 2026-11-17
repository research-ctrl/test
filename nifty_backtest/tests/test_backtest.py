"""Unit tests for backtest.py.  Run:  python -m pytest -q tests

The synthetic numbers below exist only to check arithmetic; they are never used as market data.
"""
import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backtest as bt  # noqa: E402


# --------------------------------------------------------------------------- indicators
def test_true_range_hand_example():
    df = pd.DataFrame({"high": [105.0, 110.0, 107.0], "low": [95.0, 101.0, 96.0],
                       "close": [100.0, 108.0, 97.0]})
    tr = bt.true_range(df["high"], df["low"], df["close"].shift(1))
    assert math.isnan(tr[0])          # no previous close -> not a valid TR
    assert tr[1] == 10.0              # max(9, |110-100|, |101-100|)
    assert tr[2] == 12.0              # max(11, |107-108|, |96-108|)


def test_wilder_atr_seed_and_recursion():
    tr = pd.Series([np.nan] + [float(x) for x in range(1, 21)])
    atr = bt.wilder_atr(tr, 14)
    assert atr.iloc[:14].isna().all()
    assert atr[14] == pytest.approx(7.5)                     # mean of the first 14 valid TRs (1..14)
    assert atr[15] == pytest.approx((13 * 7.5 + 15) / 14)    # Wilder: (13*prev + TR) / 14
    expected = 7.5
    for i in range(15, 21):
        expected = (13 * expected + tr[i]) / 14
        assert atr[i] == pytest.approx(expected)


def test_wilder_atr_rejects_gaps():
    tr = pd.Series([np.nan] + [1.0] * 15 + [np.nan] + [1.0] * 3)
    with pytest.raises(ValueError):
        bt.wilder_atr(tr, 14)


def test_vix_move_formula():
    df = pd.DataFrame({"date": [dt.date(2026, 1, 1)], "session_type": ["regular"], "open": [25000.0],
                       "high": [25100.0], "low": [24900.0], "close": [25000.0], "vix_open": [16.0],
                       "vix_high": [16.0], "vix_low": [16.0], "vix_close": [16.0]})
    out = bt.add_indicators(df)
    assert out["vix_move"][0] == pytest.approx(25000 * 0.16 / math.sqrt(252))


# --------------------------------------------------------------------------- calendar
def test_next_session_handles_holidays_and_muhurat():
    hol, spc = bt.load_calendar()
    assert bt.next_session(dt.date(2026, 10, 16), False, hol, spc) == dt.date(2026, 10, 19)
    assert bt.next_session(dt.date(2026, 10, 19), False, hol, spc) == dt.date(2026, 10, 21)  # 20 Oct Dussehra
    assert bt.next_session(dt.date(2026, 11, 6), False, hol, spc) == dt.date(2026, 11, 9)    # skip Muhurat
    assert bt.next_session(dt.date(2026, 11, 6), True, hol, spc) == dt.date(2026, 11, 8)     # Muhurat Sunday
    assert bt.next_session(dt.date(2026, 11, 9), False, hol, spc) == dt.date(2026, 11, 11)   # 10 Nov holiday
    assert bt.next_session(dt.date(2026, 11, 16), False, hol, spc) == dt.date(2026, 11, 17)


def test_data_gap_is_detected():
    s = bt.load_sessions()
    s = s[s["date"] != dt.date(2026, 10, 27)].reset_index(drop=True)
    with pytest.raises(ValueError, match="data gap"):
        bt.build_forecasts(bt.add_indicators(s), include_special=False)


# --------------------------------------------------------------------------- models + scoring
def test_model_formulas_on_a_real_row():
    fc = bt.build_forecasts(bt.add_indicators(bt.load_sessions()), False)
    r = fc[fc["forecast_date"] == dt.date(2026, 11, 13)].iloc[0]
    c, h, l = r["prev_close"], r["prev_high"], r["prev_low"]
    assert r["A_Camarilla_R4S4__pred_high"] == pytest.approx(c + 0.55 * (h - l))
    assert r["A_Camarilla_R4S4__pred_low"] == pytest.approx(c - 0.55 * (h - l))
    assert r["B_ATR_only__pred_high"] == pytest.approx(c + r["atr14"])
    assert r["C_VIX_only__pred_low"] == pytest.approx(c - c * r["india_vix"] / 100 / math.sqrt(252))
    assert r["D_PrevDay_HL__pred_high"] == h and r["D_PrevDay_HL__pred_low"] == l
    m = 0.5 * r["atr14"] + 0.5 * r["vix_move"]
    assert r["E_Hybrid_V1__pred_high"] == pytest.approx(c + m)
    assert r["E_Hybrid_V1__pred_low"] == pytest.approx(c - m)


def test_scoring_flags_errors_and_interval_score():
    fc = pd.DataFrame({"forecast_date": [dt.date(2026, 1, 1)], "target_date": [dt.date(2026, 1, 2)],
                       "prev_close": [100.0], "prev_high": [101.0], "prev_low": [99.0], "atr14": [10.0],
                       "india_vix": [15.0], "vix_move": [10.0], "hybrid_m": [10.0], "actual_open": [100.0],
                       "actual_high": [112.0], "actual_low": [95.0], "actual_close": [111.0],
                       "target_vix_close": [15.0], "target_vix_high": [16.0]})
    for m in bt.MODELS:
        fc[f"{m}__pred_high"], fc[f"{m}__pred_low"] = 110.0, 90.0
    s = bt.score(fc, dt.date(2026, 1, 1), dt.date(2026, 1, 31))
    r = s[s["model"] == "E_Hybrid_V1"].iloc[0]
    assert not r["high_inside"] and r["low_inside"] and not r["both_inside"]
    assert r["err_high"] == 2 and r["err_low"] == 5 and r["breakout_up"] == 2 and r["breakout_down"] == 0
    assert r["pred_width"] == 20 and r["actual_range"] == 17
    assert r["interval_score"] == pytest.approx(20 + (2 / 0.10) * 2)


def test_pending_session_is_not_scored():
    fc = pd.DataFrame({"forecast_date": [dt.date(2026, 1, 1)], "target_date": [dt.date(2026, 1, 2)],
                       "prev_close": [100.0], "prev_high": [101.0], "prev_low": [99.0], "atr14": [10.0],
                       "india_vix": [15.0], "vix_move": [10.0], "hybrid_m": [10.0], "actual_open": [np.nan],
                       "actual_high": [np.nan], "actual_low": [np.nan], "actual_close": [np.nan],
                       "target_vix_close": [np.nan], "target_vix_high": [np.nan]})
    for m in bt.MODELS:
        fc[f"{m}__pred_high"], fc[f"{m}__pred_low"] = 110.0, 90.0
    s = bt.score(fc, dt.date(2026, 1, 1), dt.date(2026, 1, 31))
    assert not s["scored"].any() and s["both_inside"].isna().all()


def test_wilson_interval():
    lo, hi = bt.wilson(15, 20)
    assert lo == pytest.approx(0.5313, abs=1e-3) and hi == pytest.approx(0.8881, abs=1e-3)


# --------------------------------------------------------------------------- no look-ahead
PRED_COLS = [f"{m}__pred_{side}" for m in bt.MODELS for side in ("high", "low")]


@pytest.mark.parametrize("include_special", [False, True])
def test_no_lookahead_truncation(include_special):
    """Forecast for every test target computed from data truncated at the forecast date
    must equal the forecast computed from the full dataset."""
    sessions = bt.load_sessions(include_special=include_special)
    full = bt.build_forecasts(bt.add_indicators(sessions), include_special).set_index("target_date")
    targets = [d for d in full.index if bt.TEST_START <= d <= bt.TEST_END]
    assert len(targets) >= 19
    for t in targets:
        p = full.loc[t, "forecast_date"]
        trunc = sessions[sessions["date"] <= p].reset_index(drop=True)
        fc_t = bt.build_forecasts(bt.add_indicators(trunc), include_special).set_index("target_date")
        pd.testing.assert_series_equal(fc_t.loc[t, PRED_COLS].astype(float),
                                       full.loc[t, PRED_COLS].astype(float), check_names=False)


def test_no_lookahead_corruption():
    """Corrupting every value on/after the target date must not change that target's forecast."""
    sessions = bt.load_sessions()
    base = bt.build_forecasts(bt.add_indicators(sessions), False).set_index("target_date")
    t = dt.date(2026, 11, 2)
    bad = sessions.copy()
    mask = bad["date"] >= t
    rng = np.random.default_rng(0)
    for c in ["open", "high", "low", "close", "vix_open", "vix_high", "vix_low", "vix_close"]:
        bad.loc[mask, c] = bad.loc[mask, c] * rng.uniform(0.5, 1.5, mask.sum())
    alt = bt.build_forecasts(bt.add_indicators(bad), False).set_index("target_date")
    pd.testing.assert_series_equal(alt.loc[t, PRED_COLS].astype(float), base.loc[t, PRED_COLS].astype(float),
                                   check_names=False)


def test_half_width_identity_matches_scoring():
    """For bands centred on the previous close: contained <=> half-width >= required half-width."""
    fc = bt.build_forecasts(bt.add_indicators(bt.load_sessions()), False)
    sc = bt.score(fc, bt.TEST_START, bt.TEST_END)
    diag = bt.half_width_diagnostics(fc, bt.TEST_START, bt.TEST_END)
    for m in ("A_Camarilla_R4S4", "B_ATR_only", "C_VIX_only", "E_Hybrid_V1"):
        s = sc[(sc["model"] == m) & sc["scored"]]
        assert diag["models"][m]["share_contained"] == pytest.approx(s["both_inside"].astype(bool).mean())
