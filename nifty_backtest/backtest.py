#!/usr/bin/env python3
"""
backtest.py - NIFTY 50 next-session High/Low range-forecast backtest.

Strategy under test: "ATR + VIX Hybrid V1"
    TR[t]          = max(High[t]-Low[t], |High[t]-Close[t-1]|, |Low[t]-Close[t-1]|)
    ATR14[t]       = Wilder smoothing, seeded with the mean of the first 14 valid TRs,
                     then ATR[t] = (13*ATR[t-1] + TR[t]) / 14
    VIX_Move[t]    = Close[t] * (IndiaVIX_Close[t]/100) / sqrt(252)
    M[t]           = 0.50*ATR14[t] + 0.50*VIX_Move[t]
    PredHigh[t+1]  = Close[t] + M[t]          PredLow[t+1] = Close[t] - M[t]

Comparison models (same dates): A Camarilla R4/S4, B ATR-only, C VIX-only,
D previous day's High/Low, E Hybrid V1.

No look-ahead: the forecast for session s uses ONLY the row of the previous session p
(its OHLC, its ATR14 - which depends on rows <= p - and its India VIX close). The actual
High/Low of s are merged afterwards, for scoring only. tests/test_backtest.py checks this
by corrupting all data from s onward and asserting the forecast for s does not change.

Input : data/nifty50_india_vix_daily.csv   (built by fetch_data.py from NSE ind_close_all files)
Output: output/  (CSV results, comparison table, charts, summary.json, RESULTS.md)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "nifty50_india_vix_daily.csv"
CALENDAR_FILE = HERE / "data" / "nse_trading_calendar_2026.json"
OUT_DIR = HERE / "output"

# ---- strategy parameters: fixed before the test, NOT tuned on October-November results ----
ATR_PERIOD = 14
W_ATR = 0.50
W_VIX = 0.50
ANNUAL_TRADING_DAYS = 252
CAMARILLA_MULT = 0.55

# ---- evaluation settings (also fixed in advance) ----
TEST_START, TEST_END = dt.date(2026, 10, 18), dt.date(2026, 11, 17)
SUPP_START, SUPP_END = dt.date(2026, 8, 1), dt.date(2026, 10, 17)  # supplementary, same fixed formula
THRESHOLDS = (25, 50, 100)
ALPHA = 0.10      # interval (Winkler) score: breakout points cost 2/alpha = 20x a point of width
ALPHA_ALT = 0.20  # robustness check of the ranking: 10x
BOOT_N, SEED = 10_000, 20261117

MODELS = {  # key -> (display name, formula)
    "A_Camarilla_R4S4": ("A. Camarilla R4/S4", "Prev Close +/- 0.55 x Prev Range"),
    "B_ATR_only": ("B. ATR-only", "Prev Close +/- ATR14"),
    "C_VIX_only": ("C. VIX-only", "Prev Close +/- VIX_Move"),
    "D_PrevDay_HL": ("D. Previous-day High/Low", "Prev High / Prev Low"),
    "E_Hybrid_V1": ("E. ATR+VIX Hybrid V1", "Prev Close +/- (0.5 ATR14 + 0.5 VIX_Move)"),
}
VARIANTS = {  # key -> (include special sessions?, description)
    "regular": (False, "Primary: regular full-day sessions (1-hour Muhurat session of 8 Nov excluded)"),
    "all_sessions": (True, "Sensitivity: every official NSE session incl. the 8 Nov Muhurat session"),
}
BOOL_COLS = ["high_inside", "low_inside", "both_inside"]


# =========================================================================== data
def load_sessions(path: Path = DATA_FILE, include_special: bool = False) -> pd.DataFrame:
    raw = pd.read_csv(path)
    raw["date"] = pd.to_datetime(raw["date"]).dt.date
    if not include_special:
        raw = raw[raw["session_type"] == "regular"]
    df = raw.rename(columns={"nifty_open": "open", "nifty_high": "high",
                             "nifty_low": "low", "nifty_close": "close"})
    cols = ["date", "session_type", "open", "high", "low", "close",
            "vix_open", "vix_high", "vix_low", "vix_close"]
    return df[cols].sort_values("date").reset_index(drop=True)


def load_calendar() -> tuple[set[dt.date], set[dt.date]]:
    cal = json.loads(CALENDAR_FILE.read_text())
    return ({dt.date.fromisoformat(d) for d in cal["holidays"]},
            {dt.date.fromisoformat(d) for d in cal["special_sessions"]})


def next_session(d: dt.date, include_special: bool, holidays: set, special: set) -> dt.date:
    x = d + dt.timedelta(days=1)
    while True:
        if include_special and x in special:
            return x
        if x.weekday() < 5 and x not in holidays:
            return x
        x += dt.timedelta(days=1)


# =========================================================================== indicators
def true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series) -> pd.Series:
    tr = np.maximum.reduce([(high - low).to_numpy(float),
                            (high - prev_close).abs().to_numpy(float),
                            (low - prev_close).abs().to_numpy(float)])
    tr = pd.Series(tr, index=high.index)
    tr[prev_close.isna()] = np.nan  # no previous close -> not a valid TR observation
    return tr


def wilder_atr(tr: pd.Series, n: int = ATR_PERIOD) -> pd.Series:
    """Wilder ATR seeded with the simple mean of the first n valid TR observations."""
    v = tr.to_numpy(float)
    out = np.full(len(v), np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) < n:
        return pd.Series(out, index=tr.index)
    first = valid[0]
    if np.isnan(v[first:]).any():
        raise ValueError("gap in the True Range series after the first valid observation")
    seed = first + n - 1
    out[seed] = v[first:seed + 1].mean()
    for i in range(seed + 1, len(v)):
        out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=tr.index)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["tr"] = true_range(out["high"], out["low"], out["close"].shift(1))
    out["atr14"] = wilder_atr(out["tr"])
    out["vix_move"] = out["close"] * (out["vix_close"] / 100.0) / math.sqrt(ANNUAL_TRADING_DAYS)
    out["hybrid_m"] = W_ATR * out["atr14"] + W_VIX * out["vix_move"]
    return out


# =========================================================================== forecasts
def model_bounds(fc: pd.DataFrame) -> dict[str, tuple[pd.Series, pd.Series]]:
    """(predicted high, predicted low) per model, from forecast-date columns only."""
    rng = fc["prev_high"] - fc["prev_low"]
    c = fc["prev_close"]
    return {
        "A_Camarilla_R4S4": (c + CAMARILLA_MULT * rng, c - CAMARILLA_MULT * rng),
        "B_ATR_only": (c + fc["atr14"], c - fc["atr14"]),
        "C_VIX_only": (c + fc["vix_move"], c - fc["vix_move"]),
        "D_PrevDay_HL": (fc["prev_high"], fc["prev_low"]),
        "E_Hybrid_V1": (c + fc["hybrid_m"], c - fc["hybrid_m"]),
    }


def build_forecasts(ind: pd.DataFrame, include_special: bool) -> pd.DataFrame:
    """One forecast per session p for the next NSE session s (per the official calendar)."""
    holidays, special = load_calendar()
    dates = list(ind["date"])
    rows = []
    for i, r in enumerate(ind.itertuples(index=False)):
        target = next_session(r.date, include_special, holidays, special)
        if i + 1 < len(dates) and dates[i + 1] != target:
            raise ValueError(f"data gap: after {r.date} the next session is {target}, "
                             f"but the dataset continues with {dates[i + 1]}")
        rows.append(dict(forecast_date=r.date, target_date=target, prev_open=r.open,
                         prev_high=r.high, prev_low=r.low, prev_close=r.close, atr14=r.atr14,
                         india_vix=r.vix_close, vix_move=r.vix_move, hybrid_m=r.hybrid_m))
    fc = pd.DataFrame(rows)
    for m, (hi, lo) in model_bounds(fc).items():
        fc[f"{m}__pred_high"], fc[f"{m}__pred_low"] = hi, lo
    # outcome of the target session - merged AFTER all forecasts exist, used only for scoring
    actual = ind[["date", "open", "high", "low", "close", "vix_close", "vix_high"]].rename(columns={
        "date": "target_date", "open": "actual_open", "high": "actual_high", "low": "actual_low",
        "close": "actual_close", "vix_close": "target_vix_close", "vix_high": "target_vix_high"})
    return fc.merge(actual, on="target_date", how="left")


# =========================================================================== scoring
def score(fc: pd.DataFrame, start: dt.date, end: dt.date) -> pd.DataFrame:
    w = fc[(fc["target_date"] >= start) & (fc["target_date"] <= end)]
    base_cols = ["forecast_date", "target_date", "prev_close", "prev_high", "prev_low", "atr14",
                 "india_vix", "vix_move", "hybrid_m", "actual_open", "actual_high", "actual_low",
                 "actual_close", "target_vix_close", "target_vix_high"]
    parts = []
    for m in MODELS:
        d = w[base_cols].copy()
        d.insert(0, "model", m)
        d["pred_high"], d["pred_low"] = w[f"{m}__pred_high"], w[f"{m}__pred_low"]
        d["scored"] = d["actual_high"].notna() & d["actual_low"].notna()
        d["err_high"] = (d["pred_high"] - d["actual_high"]).abs()
        d["err_low"] = (d["pred_low"] - d["actual_low"]).abs()
        d["avg_err"] = (d["err_high"] + d["err_low"]) / 2
        d["signed_high"] = d["pred_high"] - d["actual_high"]  # + : predicted High above actual
        d["signed_low"] = d["actual_low"] - d["pred_low"]     # + : predicted Low below actual
        d["high_inside"] = (d["actual_high"] <= d["pred_high"]) & (d["actual_high"] >= d["pred_low"])
        d["low_inside"] = (d["actual_low"] >= d["pred_low"]) & (d["actual_low"] <= d["pred_high"])
        d["both_inside"] = d["high_inside"] & d["low_inside"]
        d["pred_width"] = d["pred_high"] - d["pred_low"]
        d["actual_range"] = d["actual_high"] - d["actual_low"]
        d["width_ratio"] = d["pred_width"] / d["actual_range"]
        d["breakout_up"] = (d["actual_high"] - d["pred_high"]).clip(lower=0)
        d["breakout_down"] = (d["pred_low"] - d["actual_low"]).clip(lower=0)
        d["max_breakout"] = d[["breakout_up", "breakout_down"]].max(axis=1)
        d["interval_score"] = d["pred_width"] + (2 / ALPHA) * (d["breakout_up"] + d["breakout_down"])
        d["interval_score_alt"] = d["pred_width"] + (2 / ALPHA_ALT) * (d["breakout_up"] + d["breakout_down"])
        for c in BOOL_COLS:
            d[c] = d[c].astype("boolean")
            d.loc[~d["scored"], c] = pd.NA
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def summarize(s: pd.DataFrame) -> dict:
    s = s[s["scored"]]
    n = len(s)
    k = int(s["both_inside"].sum())
    lo, hi = wilson(k, n)
    worst = s.loc[s["max_breakout"].idxmax()]
    has_breakout = worst["max_breakout"] > 0
    out = {
        "sessions": n, "successful_sessions": k, "unsuccessful_sessions": n - k,
        "both_inside_pct": 100 * k / n, "both_inside_ci95_low": 100 * lo, "both_inside_ci95_high": 100 * hi,
        "high_inside_pct": 100 * s["high_inside"].mean(), "low_inside_pct": 100 * s["low_inside"].mean(),
        "mae_high": s["err_high"].mean(), "mae_low": s["err_low"].mean(),
        "mae_avg": (s["err_high"].mean() + s["err_low"].mean()) / 2,
        "median_err_high": s["err_high"].median(), "median_err_low": s["err_low"].median(),
        "bias_high": s["signed_high"].mean(), "bias_low": s["signed_low"].mean(),
    }
    for t in THRESHOLDS:
        out[f"high_within_{t}_pct"] = 100 * (s["err_high"] <= t).mean()
        out[f"low_within_{t}_pct"] = 100 * (s["err_low"] <= t).mean()
    out.update({
        "avg_pred_width": s["pred_width"].mean(), "avg_actual_range": s["actual_range"].mean(),
        "width_to_range": s["pred_width"].mean() / s["actual_range"].mean(),
        "largest_breakout_pts": float(worst["max_breakout"]) if has_breakout else 0.0,
        "largest_breakout_date": str(worst["target_date"]) if has_breakout else "",
        "largest_breakout_side": ("above predicted High" if worst["breakout_up"] >= worst["breakout_down"]
                                  else "below predicted Low") if has_breakout else "",
        "breakout_sessions": int((s["max_breakout"] > 0).sum()),
        "mean_breakout_pts_per_session": (s["breakout_up"] + s["breakout_down"]).mean(),
        "interval_score": s["interval_score"].mean(), "interval_score_alt": s["interval_score_alt"].mean(),
    })
    return out


def rank_models(summ: dict[str, dict]) -> pd.DataFrame:
    """Rank on two criteria that do NOT reward an over-wide band:
       (1) boundary MAE (mean of High and Low MAE): too wide or too narrow both increase it;
       (2) interval score = width + 20 x breakout points: charges for width AND for misses.
       Overall rank = mean of the two ranks (ties -> lower interval score)."""
    t = pd.DataFrame(summ).T
    t["rank_mae"] = t["mae_avg"].astype(float).rank(method="min")
    t["rank_interval"] = t["interval_score"].astype(float).rank(method="min")
    t["rank_interval_alt"] = t["interval_score_alt"].astype(float).rank(method="min")
    t["rank_containment"] = t["both_inside_pct"].astype(float).rank(method="min", ascending=False)
    t["composite"] = (t["rank_mae"] + t["rank_interval"]) / 2
    t = t.sort_values(["composite", "interval_score"])
    t["overall_rank"] = np.arange(1, len(t) + 1)
    return t


def paired_compare(sc: pd.DataFrame, a: str, b: str, metric: str) -> dict:
    """Paired comparison of model a vs model b on a per-session metric (lower is better)."""
    x = sc[(sc["model"] == a) & sc["scored"]].set_index("target_date")[metric]
    y = sc[(sc["model"] == b) & sc["scored"]].set_index("target_date")[metric]
    diff = (x - y.reindex(x.index)).to_numpy(float)
    rng = np.random.default_rng(SEED)
    boots = diff[rng.integers(0, len(diff), size=(BOOT_N, len(diff)))].mean(axis=1)
    return {"metric": metric, "a": a, "b": b, "n": len(diff), "mean_diff_a_minus_b": diff.mean(),
            "ci95_low": float(np.percentile(boots, 2.5)), "ci95_high": float(np.percentile(boots, 97.5)),
            "sessions_a_better": int((diff < 0).sum()), "sessions_b_better": int((diff > 0).sum()),
            "ties": int((diff == 0).sum())}


def containment_switches(sc: pd.DataFrame, a: str, b: str) -> dict:
    x = sc[(sc["model"] == a) & sc["scored"]].set_index("target_date")["both_inside"]
    y = sc[(sc["model"] == b) & sc["scored"]].set_index("target_date")["both_inside"].reindex(x.index)
    return {"only_a_contained": [str(d) for d in x.index[(x & ~y).fillna(False)]],
            "only_b_contained": [str(d) for d in x.index[(~x & y).fillna(False)]]}


def _spearman(a: pd.Series, b: pd.Series) -> float:
    return float(np.corrcoef(a.rank().to_numpy(float), b.rank().to_numpy(float))[0, 1])


def half_width_diagnostics(fc: pd.DataFrame, start: dt.date, end: dt.date) -> dict:
    """Parameter-free check of how well each symmetric band's half-width anticipates the
    half-width that would have been REQUIRED to contain the session:
        required = max(High - PrevClose, PrevClose - Low)   (contained  <=>  half-width >= required)."""
    w = fc[(fc["target_date"] >= start) & (fc["target_date"] <= end) & fc["actual_high"].notna()]
    req = np.maximum(w["actual_high"] - w["prev_close"], w["prev_close"] - w["actual_low"])
    hw = {"A_Camarilla_R4S4": CAMARILLA_MULT * (w["prev_high"] - w["prev_low"]), "B_ATR_only": w["atr14"],
          "C_VIX_only": w["vix_move"], "E_Hybrid_V1": w["hybrid_m"]}
    out = {"window": [str(start), str(end)], "n": int(len(w)), "required_mean": float(req.mean()),
           "required_median": float(req.median()), "models": {}}
    for m, h in hw.items():
        out["models"][m] = {"mean_half_width": float(h.mean()), "spearman_vs_required": _spearman(h, req),
                            "share_contained": float((h >= req).mean())}
    return out


def vix_before_failures(sc: pd.DataFrame, model: str = "E_Hybrid_V1") -> dict:
    s = sc[(sc["model"] == model) & sc["scored"]]
    fail = ~s["both_inside"].astype(bool)
    return {"failures": int(fail.sum()), "successes": int((~fail).sum()),
            "mean_vix_fcst_day_failures": float(s.loc[fail, "india_vix"].mean()),
            "mean_vix_fcst_day_successes": float(s.loc[~fail, "india_vix"].mean()),
            "mean_vix_move_failures": float(s.loc[fail, "vix_move"].mean()),
            "mean_vix_move_successes": float(s.loc[~fail, "vix_move"].mean())}


def failure_table(sc: pd.DataFrame, model: str = "E_Hybrid_V1") -> pd.DataFrame:
    s = sc[(sc["model"] == model) & sc["scored"] & ~sc["both_inside"].fillna(True)].copy()
    s["open_outside_band"] = np.where((s["actual_open"] > s["pred_high"]) | (s["actual_open"] < s["pred_low"]),
                                      "Yes", "No")
    s["gap_open_pts"] = s["actual_open"] - s["prev_close"]
    s["close_change_pct"] = 100 * (s["actual_close"] / s["prev_close"] - 1)
    s["range_vs_atr"] = s["actual_range"] / s["atr14"]
    s["vix_change"] = s["target_vix_close"] - s["india_vix"]
    s["side"] = np.where(s["breakout_up"] >= s["breakout_down"], "above High", "below Low")
    return s.sort_values("max_breakout", ascending=False)


def atr_seed_sensitivity(include_special: bool, starts: list[dt.date]) -> dict:
    """How much does starting the data later (different Wilder seed) move ATR14 in the test window?"""
    full = load_sessions(include_special=include_special)
    base = add_indicators(full).set_index("date")["atr14"]
    test_fc_dates = build_forecasts(add_indicators(full), include_special)
    test_fc_dates = test_fc_dates[(test_fc_dates["target_date"] >= TEST_START) &
                                  (test_fc_dates["target_date"] <= TEST_END)]["forecast_date"]
    res = {}
    for st in starts:
        alt = add_indicators(full[full["date"] >= st].reset_index(drop=True)).set_index("date")["atr14"]
        d = (alt.reindex(test_fc_dates) - base.reindex(test_fc_dates)).abs()
        res[str(st)] = {"max_abs_atr_diff_pts": float(d.max()), "mean_abs_atr_diff_pts": float(d.mean())}
    return res


# =========================================================================== reporting helpers
def yes_no(v) -> str:
    return "" if pd.isna(v) else ("Yes" if bool(v) else "No")


def hybrid_daily_table(sc: pd.DataFrame) -> pd.DataFrame:
    h = sc[sc["model"] == "E_Hybrid_V1"].copy()
    t = pd.DataFrame({
        "Forecast date": h["forecast_date"].astype(str),
        "Trading date predicted": h["target_date"].astype(str),
        "Previous Close": h["prev_close"].round(2),
        "ATR14": h["atr14"].round(2),
        "India VIX": h["india_vix"].round(4),
        "VIX_Move": h["vix_move"].round(2),
        "M": h["hybrid_m"].round(2),
        "Predicted High": h["pred_high"].round(2),
        "Actual High": h["actual_high"].round(2),
        "Predicted Low": h["pred_low"].round(2),
        "Actual Low": h["actual_low"].round(2),
        "Abs High error (pts)": h["err_high"].round(2),
        "Abs Low error (pts)": h["err_low"].round(2),
        "Actual High inside range?": h["high_inside"].map(yes_no),
        "Actual Low inside range?": h["low_inside"].map(yes_no),
        "Both extremes inside range?": h["both_inside"].map(yes_no),
        "Predicted width (pts)": h["pred_width"].round(2),
        "Actual range (pts)": h["actual_range"].round(2),
        "Width / actual range": h["width_ratio"].round(2),
        "Breakout above High (pts)": h["breakout_up"].round(2),
        "Breakout below Low (pts)": h["breakout_down"].round(2),
        "Status": np.where(h["scored"], "scored", "PENDING - official NSE data not available at run time"),
    })
    return t.reset_index(drop=True)


def md_table(df: pd.DataFrame, floatfmt: str = "{:,.2f}") -> str:
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else floatfmt.format(v)
        return str(v)
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    body = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def comparison_view(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m, r in t.iterrows():
        rows.append({
            "Rank": int(r["overall_rank"]), "Model": MODELS[m][0], "Sessions": int(r["sessions"]),
            "Both inside %": f"{r['both_inside_pct']:.1f}",
            "95% CI": f"{r['both_inside_ci95_low']:.0f}-{r['both_inside_ci95_high']:.0f}",
            "High inside %": f"{r['high_inside_pct']:.1f}", "Low inside %": f"{r['low_inside_pct']:.1f}",
            "MAE High": f"{r['mae_high']:.1f}", "MAE Low": f"{r['mae_low']:.1f}",
            "High <=25/50/100 %": f"{r['high_within_25_pct']:.0f}/{r['high_within_50_pct']:.0f}/{r['high_within_100_pct']:.0f}",
            "Low <=25/50/100 %": f"{r['low_within_25_pct']:.0f}/{r['low_within_50_pct']:.0f}/{r['low_within_100_pct']:.0f}",
            "Avg width": f"{r['avg_pred_width']:.1f}", "Avg actual range": f"{r['avg_actual_range']:.1f}",
            "Width/range": f"{r['width_to_range']:.2f}",
            "Largest breakout": (f"{r['largest_breakout_pts']:.1f} ({r['largest_breakout_date']}, "
                                 f"{r['largest_breakout_side']})" if r["largest_breakout_pts"] > 0 else "none"),
            "Success/Fail": f"{int(r['successful_sessions'])}/{int(r['unsuccessful_sessions'])}",
            "Interval score": f"{r['interval_score']:.1f}",
        })
    return pd.DataFrame(rows)


# =========================================================================== main
def run(make_charts: bool = True) -> dict:
    OUT_DIR.mkdir(exist_ok=True)
    summary: dict = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "parameters": {"atr_period": ATR_PERIOD, "w_atr": W_ATR, "w_vix": W_VIX,
                       "annual_trading_days": ANNUAL_TRADING_DAYS, "camarilla_mult": CAMARILLA_MULT,
                       "test_window": [str(TEST_START), str(TEST_END)], "interval_alpha": ALPHA,
                       "interval_alpha_alt": ALPHA_ALT},
        "variants": {},
    }
    all_scores, comparisons = [], []
    for vkey, (inc_special, vdesc) in VARIANTS.items():
        sessions = load_sessions(include_special=inc_special)
        ind = add_indicators(sessions)
        fc = build_forecasts(ind, inc_special)
        sc = score(fc, TEST_START, TEST_END)
        sc.insert(0, "variant", vkey)
        all_scores.append(sc)

        summ = {m: summarize(sc[sc["model"] == m]) for m in MODELS}
        ranked = rank_models(summ)
        cmp_rows = ranked.copy()
        cmp_rows.insert(0, "model_name", [MODELS[m][0] for m in cmp_rows.index])
        cmp_rows.insert(0, "variant", vkey)
        comparisons.append(cmp_rows.reset_index(names="model"))

        seed_row = ind[ind["atr14"].notna()].iloc[0]
        first_tr = ind[ind["tr"].notna()].iloc[0]
        pending = sc[(sc["model"] == "E_Hybrid_V1") & ~sc["scored"]]
        vs = {
            "description": vdesc,
            "data_rows": len(sessions), "data_first": str(sessions["date"].iloc[0]),
            "data_last": str(sessions["date"].iloc[-1]),
            "first_valid_tr": str(first_tr["date"]), "atr_seed_date": str(seed_row["date"]),
            "atr_seed_value": float(seed_row["atr14"]),
            "test_targets": [str(d) for d in sc[sc["model"] == "E_Hybrid_V1"]["target_date"]],
            "pending_targets": [str(d) for d in pending["target_date"]],
            "pending_forecasts": [{k: (str(v) if isinstance(v, dt.date) else round(float(v), 2))
                                   for k, v in r.items()} for r in
                                  pending[["forecast_date", "target_date", "prev_close", "atr14",
                                           "india_vix", "vix_move", "hybrid_m", "pred_high",
                                           "pred_low"]].to_dict("records")],
            "metrics": summ, "ranking": [m for m in ranked.index],
            "paired": [paired_compare(sc, "E_Hybrid_V1", b, met)
                       for b in ("B_ATR_only", "C_VIX_only") for met in ("avg_err", "interval_score")],
            "containment_switches": {b: containment_switches(sc, "E_Hybrid_V1", b)
                                     for b in ("B_ATR_only", "C_VIX_only")},
            "atr_seed_sensitivity": atr_seed_sensitivity(inc_special, [dt.date(2026, 6, 29),
                                                                       dt.date(2026, 7, 15)]),
        }
        summary["variants"][vkey] = vs

        if vkey == "regular":
            hybrid_daily_table(sc).to_csv(OUT_DIR / "hybrid_v1_daily_results.csv", index=False)
            fails = failure_table(sc)
            summary["diagnostics"] = {
                "half_width_test": half_width_diagnostics(fc, TEST_START, TEST_END),
                "half_width_aug_to_nov": half_width_diagnostics(fc, SUPP_START, TEST_END),
                "vix_before_failures": vix_before_failures(sc),
            }
            sup = score(fc, SUPP_START, SUPP_END)
            sup_summ = {m: summarize(sup[sup["model"] == m]) for m in MODELS}
            sup_ranked = rank_models(sup_summ)
            sup["month"] = pd.to_datetime(sup["target_date"]).dt.strftime("%Y-%m")
            monthly = []
            for (mth, m), g in sup[sup["scored"]].groupby(["month", "model"]):
                r = summarize(g)
                monthly.append({"month": mth, "model": m, "sessions": r["sessions"],
                                "both_inside_pct": r["both_inside_pct"], "mae_avg": r["mae_avg"],
                                "width_to_range": r["width_to_range"], "interval_score": r["interval_score"]})
            monthly = pd.DataFrame(monthly)
            monthly.to_csv(OUT_DIR / "supplementary_monthly.csv", index=False)
            summary["supplementary"] = {"window": [str(SUPP_START), str(SUPP_END)], "metrics": sup_summ,
                                        "ranking": list(sup_ranked.index)}
            pooled = score(fc, SUPP_START, TEST_END)
            summary["pooled_aug_to_test_end"] = {"window": [str(SUPP_START), str(TEST_END)],
                                                 "metrics": {m: summarize(pooled[pooled["model"] == m])
                                                             for m in MODELS}}
            if make_charts:
                import importlib.util  # load the sibling module explicitly (works under python -I)
                spec = importlib.util.spec_from_file_location("charts", HERE / "charts.py")
                charts = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(charts)
                charts.hybrid_chart(sc, OUT_DIR / "chart_hybrid_v1.png", summ["E_Hybrid_V1"])
                charts.all_models_chart(sc, OUT_DIR / "chart_all_models.png", summ, MODELS)
            primary = dict(sc=sc, ranked=ranked, fails=fails, sup_ranked=sup_ranked, monthly=monthly)
        else:
            hybrid_daily_table(sc).to_csv(OUT_DIR / "hybrid_v1_daily_results_incl_muhurat.csv", index=False)
            sens = dict(sc=sc, ranked=ranked)

    scores = pd.concat(all_scores, ignore_index=True)
    scores.to_csv(OUT_DIR / "all_models_daily_results.csv", index=False, float_format="%.4f")
    comp = pd.concat(comparisons, ignore_index=True)
    comp.to_csv(OUT_DIR / "model_comparison.csv", index=False, float_format="%.4f")
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    write_results_md(summary, primary, sens)
    return summary


def write_results_md(summary: dict, primary: dict, sens: dict) -> None:
    v = summary["variants"]["regular"]
    hm = v["metrics"]["E_Hybrid_V1"]
    L = ["# Backtest results (generated by backtest.py - do not edit by hand)", "",
         f"Generated {summary['generated_utc']} UTC. Test window: forecast targets "
         f"{TEST_START} to {TEST_END}. Data: {v['data_first']} to {v['data_last']} "
         f"({v['data_rows']} regular sessions). First valid TR {v['first_valid_tr']}; "
         f"ATR14 seeded on {v['atr_seed_date']} ({v['atr_seed_value']:.2f}).", ""]
    if v["pending_targets"]:
        L += [f"**Pending (not scored):** {', '.join(v['pending_targets'])} - official NSE file not yet "
              "available at run time. Forecast shown, actuals left blank (nothing estimated).", ""]
    L += ["## 1. ATR + VIX Hybrid V1 - daily results (primary: regular sessions)", ""]
    daily = hybrid_daily_table(primary["sc"]).drop(columns=["VIX_Move", "M", "Status"])
    daily.columns = ["Forecast", "Target", "Prev Close", "ATR14", "VIX", "Pred High", "Act High",
                     "Pred Low", "Act Low", "Abs err H", "Abs err L", "H in?", "L in?", "Both in?",
                     "Width", "Act range", "W/R", "Brk up", "Brk dn"]
    L += [md_table(daily), ""]
    L += ["## 2. Hybrid V1 headline metrics", "",
          "| Metric | Primary (regular) | Incl. Muhurat |", "|---|---|---|"]
    hs = summary["variants"]["all_sessions"]["metrics"]["E_Hybrid_V1"]
    def both(fmt, key):
        return f"| {fmt} | {hm[key]:.2f} | {hs[key]:.2f} |"
    L += [f"| Sessions scored | {hm['sessions']} | {hs['sessions']} |",
          f"| Both extremes inside (%) | {hm['both_inside_pct']:.1f} (95% CI {hm['both_inside_ci95_low']:.0f}-"
          f"{hm['both_inside_ci95_high']:.0f}) | {hs['both_inside_pct']:.1f} |",
          f"| Successful / unsuccessful | {hm['successful_sessions']} / {hm['unsuccessful_sessions']} | "
          f"{hs['successful_sessions']} / {hs['unsuccessful_sessions']} |",
          both("High inside (%)", "high_inside_pct"), both("Low inside (%)", "low_inside_pct"),
          both("MAE High (pts)", "mae_high"), both("MAE Low (pts)", "mae_low"),
          both("Avg predicted width (pts)", "avg_pred_width"), both("Avg actual range (pts)", "avg_actual_range"),
          both("Width / range", "width_to_range"), both("Largest breakout (pts)", "largest_breakout_pts"), ""]
    L += ["## 3. Five-model comparison - primary (regular sessions)", "",
          "Ranking = mean of rank(boundary MAE) and rank(interval score, alpha=0.10). Both criteria "
          "penalise an over-wide band, so a model cannot win just by containing more.", "",
          md_table(comparison_view(primary["ranked"])), ""]
    L += ["## 4. Five-model comparison - sensitivity (incl. 8 Nov Muhurat session)", "",
          md_table(comparison_view(sens["ranked"])), ""]
    r = primary["ranked"]
    L += ["## 5. Ranking robustness", "", "| Model | rank MAE | rank interval a=0.10 | rank interval a=0.20 | "
          "rank containment | overall |", "|---|---|---|---|---|---|"]
    for m, row in r.iterrows():
        L.append(f"| {MODELS[m][0]} | {int(row['rank_mae'])} | {int(row['rank_interval'])} | "
                 f"{int(row['rank_interval_alt'])} | {int(row['rank_containment'])} | {int(row['overall_rank'])} |")
    L += ["", "## 6. Did India VIX help? Paired per-session comparison (primary)", "",
          "| Comparison | Metric | Mean diff (Hybrid - other) | Bootstrap 95% CI | Hybrid better / worse / tie |",
          "|---|---|---|---|---|"]
    for p in v["paired"]:
        L.append(f"| Hybrid vs {MODELS[p['b']][0]} | {p['metric']} | {p['mean_diff_a_minus_b']:+.2f} | "
                 f"{p['ci95_low']:+.2f} to {p['ci95_high']:+.2f} | {p['sessions_a_better']} / "
                 f"{p['sessions_b_better']} / {p['ties']} |")
    for b, sw in v["containment_switches"].items():
        L.append(f"\nContained by Hybrid only vs {MODELS[b][0]}: {', '.join(sw['only_a_contained']) or 'none'}; "
                 f"contained by {MODELS[b][0]} only: {', '.join(sw['only_b_contained']) or 'none'}.")
    f = primary["fails"]
    L += ["", "## 7. Hybrid V1 failures (range not fully inside the band), worst first", ""]
    if len(f):
        ft = pd.DataFrame({
            "Target": f["target_date"].astype(str), "Side": f["side"],
            "Breakout (pts)": f["max_breakout"].round(2), "Opened outside band?": f["open_outside_band"],
            "Act range": f["actual_range"].round(2),
            "ATR14": f["atr14"].round(2), "Range/ATR": f["range_vs_atr"].round(2),
            "Gap at open": f["gap_open_pts"].round(2), "Close chg %": f["close_change_pct"].round(2),
            "VIX (fcst day)": f["india_vix"].round(2), "VIX (target day)": f["target_vix_close"].round(2),
            "VIX chg": f["vix_change"].round(2), "VIX intraday high": f["target_vix_high"].round(2)})
        L += [md_table(ft), ""]
    else:
        L += ["None.", ""]
    L += ["## 8. Supplementary check - same fixed formulas on the preceding period", "",
          f"Forecast targets {SUPP_START} to {SUPP_END} (not part of the requested test; shown only to "
          "judge stability). No parameter was changed.", "",
          md_table(comparison_view(primary["sup_ranked"])), ""]
    mo = primary["monthly"].copy()
    mo["model"] = mo["model"].map(lambda m: MODELS[m][0])
    mo = mo.rename(columns={"both_inside_pct": "both inside %", "mae_avg": "boundary MAE",
                            "width_to_range": "width/range", "interval_score": "interval score"})
    L += ["Monthly breakdown:", "", md_table(mo), ""]
    pm = summary["pooled_aug_to_test_end"]
    L += [f"Pooled supplementary + test window ({pm['window'][0]} to {pm['window'][1]}, scored sessions only):", "",
          "| Model | Sessions | Both inside % (95% CI) | Boundary MAE | Width/range | Interval score |",
          "|---|---|---|---|---|---|"]
    for m, r in pm["metrics"].items():
        L.append(f"| {MODELS[m][0]} | {r['sessions']} | {r['both_inside_pct']:.1f} ({r['both_inside_ci95_low']:.0f}-"
                 f"{r['both_inside_ci95_high']:.0f}) | {r['mae_avg']:.1f} | {r['width_to_range']:.2f} | "
                 f"{r['interval_score']:.1f} |")
    L.append("")
    dg = summary["diagnostics"]
    L += ["## 9. Diagnostics - does India VIX add information beyond ATR?", "",
          "For a band centred on the previous close, a session is fully contained exactly when the predicted "
          "half-width >= required half-width = max(High - PrevClose, PrevClose - Low). The rank correlation "
          "between predicted and required half-width measures whether a model widens on the right days "
          "(timing), independently of how wide it is on average (level). No parameters involved.", "",
          "| Window | Model | Mean predicted half-width | Spearman vs required | Share contained |",
          "|---|---|---|---|---|"]
    for key in ("half_width_test", "half_width_aug_to_nov"):
        h = dg[key]
        for m, d in h["models"].items():
            L.append(f"| {h['window'][0]} to {h['window'][1]} (n={h['n']}, required mean "
                     f"{h['required_mean']:.1f} / median {h['required_median']:.1f}) | {MODELS[m][0]} | "
                     f"{d['mean_half_width']:.1f} | {d['spearman_vs_required']:+.2f} | {100 * d['share_contained']:.1f}% |")
    vb = dg["vix_before_failures"]
    L += ["", f"India VIX at the forecast-day close before Hybrid failures: mean {vb['mean_vix_fcst_day_failures']:.2f} "
          f"({vb['failures']} sessions) vs before successes: {vb['mean_vix_fcst_day_successes']:.2f} "
          f"({vb['successes']} sessions).", ""]
    L += ["## 10. ATR warm-up sensitivity", "",
          "Effect on ATR14 at the test-window forecast dates if the data had started later "
          "(i.e. a different Wilder seed):", ""]
    for st, d in v["atr_seed_sensitivity"].items():
        L.append(f"* data from {st}: max |dATR14| = {d['max_abs_atr_diff_pts']:.3f} pts, "
                 f"mean = {d['mean_abs_atr_diff_pts']:.3f} pts")
    (OUT_DIR / "RESULTS.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="NIFTY 50 range-forecast backtest")
    ap.add_argument("--no-charts", action="store_true")
    a = ap.parse_args()
    s = run(make_charts=not a.no_charts)
    m = s["variants"]["regular"]["metrics"]["E_Hybrid_V1"]
    print(f"Hybrid V1 (regular sessions): {m['sessions']} scored, both-inside {m['both_inside_pct']:.1f}%, "
          f"MAE High {m['mae_high']:.1f}, MAE Low {m['mae_low']:.1f}")
    print("Ranking:", " > ".join(s["variants"]["regular"]["ranking"]))
    print("Outputs written to", OUT_DIR)
