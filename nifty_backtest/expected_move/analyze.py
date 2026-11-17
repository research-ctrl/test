#!/usr/bin/env python3
"""
analyze.py - do the two "expected move" reels hold up on real NIFTY expiries?

Reel 1  Expected move to expiry = Spot x (VIX/100) x sqrt(days to expiry / 365),
        or the "easy trick" ATM call + ATM put premium x 1.25.
        Claim: the market closes inside Spot +/- expected move 68% of the time.
Reel 2  "Nifty probability calculator": P(Nifty below K at expiry) = N( ln(K/Spot) / ((VIX/100) sqrt(DTE/365)) ).
        Claim: e.g. 93% probability Nifty stays below the chosen call strike -> "safe zone" to write calls
        (and the mirror image for puts below the market).

Both reels use the same model, so one quantity tests every claim at once:
    z = ln(Close_at_expiry / Spot) / ((VIX/100) * sqrt(DTE/365))
If the model were right, z would be standard normal: |z| <= 1 on 68% of occasions, z < 1.476 on 93%, ...

Data: data/nifty_vix_daily_2019_2026.csv (official NSE daily index files, verified by build_history.py),
      data/nifty_atm_straddle_2026.csv (official NSE F&O bhavcopy, 3 Aug - 13 Nov 2026).
Weekly expiries: Thursday from 14 Feb 2019 (start of NIFTY weekly options) to 28 Aug 2025, Tuesday from
1 Sep 2025; monthly: last Thursday / last Tuesday. A holiday moves expiry to the previous trading day.
The calendar is checked against the expiries listed in NSE's 2026 F&O files.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA, OUT = HERE / "data", HERE / "output"
N = NormalDist()
WEEKLY_START = dt.date(2019, 2, 14)   # first NIFTY weekly expiry
WEEKLY_LAUNCH = dt.date(2019, 2, 11)  # first day NIFTY weekly options traded
TUESDAY_FROM = dt.date(2025, 9, 1)
PROBS = (0.68, 0.80, 0.90, 0.93, 0.95, 0.96, 0.98, 0.99)
BOOT, SEED = 2000, 20261117


# ----------------------------------------------------------------------------- data + calendars
def load_history() -> pd.DataFrame:
    h = pd.read_csv(DATA / "nifty_vix_daily_2019_2026.csv", parse_dates=["date"])
    h["date"] = h["date"].dt.date
    h = h[h["session_type"] == "regular"].reset_index(drop=True)
    h["vix_valid"] = h["vix_open"].notna()  # NSE published no fresh VIX on two days in 2021
    return h


def expiry_calendars(trading_days: list[dt.date], last: dt.date) -> tuple[list[dt.date], list[dt.date]]:
    tdays = sorted(trading_days)

    def on_or_before(day: dt.date, after: dt.date) -> dt.date | None:
        c = [t for t in tdays if after < t <= day]
        return c[-1] if c else None

    weekly, d = [], WEEKLY_START
    while d <= last:
        e = on_or_before(d, d - dt.timedelta(days=7))
        if e:
            weekly.append(e)
        nxt = d + dt.timedelta(days=7)
        if d < TUESDAY_FROM <= nxt:  # switch from Thursday to Tuesday expiries
            nxt = TUESDAY_FROM + dt.timedelta(days=(1 - TUESDAY_FROM.weekday()) % 7)
        d = nxt
    monthly = []
    y, m = tdays[0].year, tdays[0].month
    while dt.date(y, m, 1) <= last:
        nm = dt.date(y + (m == 12), m % 12 + 1, 1)
        target_wd = 1 if dt.date(y, m, 1) >= TUESDAY_FROM else 3
        day = nm - dt.timedelta(days=1)
        while day.weekday() != target_wd:
            day -= dt.timedelta(days=1)
        if day <= last:
            e = on_or_before(day, day - dt.timedelta(days=7))
            if e:
                monthly.append(e)
        y, m = nm.year, nm.month
    return weekly, monthly


def verify_calendar(weekly: list[dt.date], monthly: list[dt.date]) -> dict:
    listed = pd.read_csv(DATA / "nifty_option_expiries_2026.csv", parse_dates=["expiry"])["expiry"].dt.date
    s = pd.read_csv(DATA / "nifty_atm_straddle_2026.csv", parse_dates=["date"])["date"].dt.date
    lo, hi = s.min(), max(weekly)
    listed_in = sorted(e for e in listed if lo < e <= hi)
    mine = sorted(e for e in weekly if lo < e <= hi)
    if listed_in != mine:
        raise SystemExit(f"expiry calendar mismatch vs NSE F&O files:\n listed {listed_in}\n mine   {mine}")
    return {"window": [str(lo), str(hi)], "weekly_expiries_matched": len(mine),
            "monthly_in_window": [str(e) for e in monthly if lo < e <= hi]}


# ----------------------------------------------------------------------------- observations
def observations(h: pd.DataFrame, expiries: list[dt.date], kind: str, start: dt.date) -> pd.DataFrame:
    h = h.set_index("date")
    dates = list(h.index)
    pos = {d: i for i, d in enumerate(dates)}
    exp = sorted(expiries)
    rows, j = [], 0
    for t in dates:
        if t < start or not h.at[t, "vix_valid"]:
            continue
        while j < len(exp) and exp[j] <= t:
            j += 1
        if j >= len(exp):
            break
        e = exp[j]
        dte = (e - t).days
        s, sig = h.at[t, "nifty_close"], h.at[t, "vix_close"] / 100
        path = h.iloc[pos[t] + 1: pos[e] + 1]
        se, hi, lo = h.at[e, "nifty_close"], path["nifty_high"].max(), path["nifty_low"].min()
        k = sig * math.sqrt(dte / 365)
        em = s * k
        rows.append({"kind": kind, "origin": t, "origin_weekday": t.strftime("%a"), "expiry": e, "dte": dte,
                     "sessions_to_expiry": len(path), "spot": s, "vix": sig * 100, "expected_move": em,
                     "close_at_expiry": se, "high_to_expiry": hi, "low_to_expiry": lo,
                     "move": se - s, "close_inside": abs(se - s) <= em,
                     "range_inside": (hi <= s + em) and (lo >= s - em),
                     "z": math.log(se / s) / k, "z_high": math.log(hi / s) / k, "z_low": math.log(lo / s) / k})
    return pd.DataFrame(rows)


def straddle_observations(h: pd.DataFrame) -> pd.DataFrame:
    st = pd.read_csv(DATA / "nifty_atm_straddle_2026.csv", parse_dates=["date", "expiry"])
    hh = h.set_index("date")
    dates = list(hh.index)
    pos = {d: i for i, d in enumerate(dates)}
    rows = []
    for r in st.itertuples(index=False):
        t, e = r.date.date(), r.expiry.date()
        if e not in pos or t not in pos:
            continue  # expiry after the last available session (17 Nov) -> outcome unknown
        path = hh.iloc[pos[t] + 1: pos[e] + 1]
        se, hi, lo = hh.at[e, "nifty_close"], path["nifty_high"].max(), path["nifty_low"].min()
        c = r.parity_implied_level
        em_s = 1.25 * r.straddle_close
        vix = hh.at[t, "vix_close"] / 100
        em_v = r.nifty_close * vix * math.sqrt(r.dte_calendar / 365)
        rows.append({"origin": t, "expiry": e, "dte": r.dte_calendar, "center_parity": c,
                     "official_close": r.nifty_close, "atm_strike": r.atm_strike, "straddle": r.straddle_close,
                     "em_straddle_x1_25": em_s, "em_vix": em_v, "close_at_expiry": se,
                     "straddle_close_inside": abs(se - c) <= em_s,
                     "straddle_range_inside": (hi <= c + em_s) and (lo >= c - em_s),
                     "vix_close_inside": abs(se - r.nifty_close) <= em_v,
                     "vix_range_inside": (hi <= r.nifty_close + em_v) and (lo >= r.nifty_close - em_v),
                     "straddle_implied_vol": 100 * r.straddle_close / (math.sqrt(2 / math.pi) * c *
                                                                       math.sqrt(r.dte_calendar / 365))})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- statistics
def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return 100 * (c - hw), 100 * (c + hw)


def cluster_ci(df: pd.DataFrame, col: str) -> tuple[float, float]:
    """95% CI of a pooled rate, resampling whole expiries (observations sharing an expiry are not independent)."""
    g = df.groupby("expiry")[col].agg(["sum", "count"]).to_numpy(float)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(g), size=(BOOT, len(g)))
    rates = g[idx, 0].sum(axis=1) / g[idx, 1].sum(axis=1)
    return 100 * np.percentile(rates, 2.5), 100 * np.percentile(rates, 97.5)


def coverage_table(obs: pd.DataFrame, by: str | None) -> pd.DataFrame:
    rows = []
    groups = [("all", obs)] if by is None else list(obs.groupby(by))
    for key, g in groups:
        k_c, k_r, n = int(g["close_inside"].sum()), int(g["range_inside"].sum()), len(g)
        ci_c = cluster_ci(g, "close_inside") if by is None else wilson(k_c, n)
        rows.append({"group": key, "observations": n, "expiries": g["expiry"].nunique(),
                     "claimed_%": 68.3, "close_inside_%": 100 * k_c / n, "close_ci95": f"{ci_c[0]:.0f}-{ci_c[1]:.0f}",
                     "whole_path_inside_%": 100 * k_r / n, "avg_expected_move_pts": g["expected_move"].mean(),
                     "median_abs_move_pts": g["move"].abs().median(),
                     "realized_to_implied_vol": math.sqrt((g["z"] ** 2).mean())})
    return pd.DataFrame(rows)


def calibration_table(obs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p in PROBS:
        zp = N.inv_cdf(p)
        rows.append({"model_probability_%": 100 * p, "z": zp,
                     "upside_close_below_strike_%": 100 * (obs["z"] < zp).mean(),
                     "upside_never_traded_above_%": 100 * (obs["z_high"] < zp).mean(),
                     "downside_close_above_strike_%": 100 * (obs["z"] > -zp).mean(),
                     "downside_never_traded_below_%": 100 * (obs["z_low"] > -zp).mean()})
    return pd.DataFrame(rows)


def yearly_table(obs: pd.DataFrame) -> pd.DataFrame:
    z93, z96 = N.inv_cdf(0.93), N.inv_cdf(0.96)
    rows = []
    for y, g in obs.groupby(pd.to_datetime(obs["origin"]).dt.year):
        rows.append({"year": y, "observations": len(g), "avg_vix": g["vix"].mean(),
                     "close_inside_1sd_%": 100 * g["close_inside"].mean(),
                     "breached_93%_call_strike_%": 100 * (g["z"] >= z93).mean(),
                     "breached_96%_put_strike_%": 100 * (g["z"] <= -z96).mean(),
                     "traded_through_93%_call_strike_%": 100 * (g["z_high"] >= z93).mean(),
                     "realized_to_implied_vol": math.sqrt((g["z"] ** 2).mean())})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- report helpers
def md(df: pd.DataFrame, fmt: str = "{:,.1f}") -> str:
    def f(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else fmt.format(v)
        return str(v)
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns),
                      *["| " + " | ".join(f(v) for v in r) + " |" for r in df.itertuples(index=False)]])


def main() -> None:
    OUT.mkdir(exist_ok=True)
    h = load_history()
    last = h["date"].max()
    weekly, monthly = expiry_calendars(list(h["date"]), last)
    cal = verify_calendar(weekly, monthly)

    wk = observations(h, weekly, "weekly", WEEKLY_LAUNCH)
    mo = observations(h, monthly, "monthly", h["date"].min())
    so = straddle_observations(h)
    pd.concat([wk, mo]).to_csv(OUT / "vix_model_observations.csv", index=False, float_format="%.4f")
    so.to_csv(OUT / "straddle_observations_2026.csv", index=False, float_format="%.4f")

    t_wk_all, t_wk_dte = coverage_table(wk, None), coverage_table(wk, "dte")
    t_mo_all = coverage_table(mo, None)
    mo = mo.assign(dte_bucket=pd.cut(mo["dte"], [0, 7, 14, 21, 40], labels=["1-7", "8-14", "15-21", "22+"]))
    t_mo_b = coverage_table(mo, "dte_bucket")
    cal_wk, cal_wk5, cal_mo = calibration_table(wk), calibration_table(wk[wk["dte"] == 5]), calibration_table(mo)
    yearly = yearly_table(wk)
    so_tab = []
    for name, g in [("all", so), *[(f"DTE {d}", x) for d, x in so.groupby("dte")]]:
        ci = cluster_ci(g, "straddle_close_inside") if name == "all" else wilson(int(g["straddle_close_inside"].sum()), len(g))
        so_tab.append({"group": name, "observations": len(g), "expiries": g["expiry"].nunique(),
                       "straddle_x1.25_close_inside_%": 100 * g["straddle_close_inside"].mean(),
                       "close_ci95": f"{ci[0]:.0f}-{ci[1]:.0f}",
                       "straddle_x1.25_path_inside_%": 100 * g["straddle_range_inside"].mean(),
                       "vix_close_inside_%": 100 * g["vix_close_inside"].mean(),
                       "avg_straddle": g["straddle"].mean(), "avg_em_straddle_x1.25": g["em_straddle_x1_25"].mean(),
                       "avg_em_vix": g["em_vix"].mean(), "avg_straddle_implied_vol": g["straddle_implied_vol"].mean(),
                       "avg_vix": (g["em_vix"] / g["official_close"] / np.sqrt(g["dte"] / 365)).mean() * 100})
    so_tab = pd.DataFrame(so_tab)
    for name, t in [("weekly_coverage_by_dte", t_wk_dte), ("weekly_calibration", cal_wk), ("monthly_calibration", cal_mo),
                    ("weekly_by_year", yearly), ("straddle_test_2026", so_tab), ("monthly_coverage_by_dte", t_mo_b)]:
        t.to_csv(OUT / f"{name}.csv", index=False, float_format="%.3f")

    # the reels' own examples
    ex1 = {"spot": 23897.70, "vix": 10.68, "days_used_in_reel": 2}
    ex1["em_reel"] = ex1["spot"] * ex1["vix"] / 100 * math.sqrt(2 / 365)
    ex1["em_calendar_days_from_friday_close"] = ex1["spot"] * ex1["vix"] / 100 * math.sqrt(4 / 365)
    srow = so[so["origin"] == dt.date(2026, 9, 4)].iloc[0]
    ex1.update({"straddle_eod_atm": float(srow["straddle"]), "atm_strike": float(srow["atm_strike"]),
                "center_parity": float(srow["center_parity"]), "em_straddle": float(srow["em_straddle_x1_25"]),
                "expiry": "2026-09-08", "close_at_expiry": float(srow["close_at_expiry"])})
    s2 = 24500 / math.exp(N.inv_cdf(0.93) * 0.19 * math.sqrt(5 / 365))
    k = 0.19 * math.sqrt(5 / 365)
    ex2 = {"implied_spot": s2, "p_below_24500": N.cdf(math.log(24500 / s2) / k),
           "p_above_22800": 1 - N.cdf(math.log(22800 / s2) / k)}

    summary = {"calendar_check": cal, "weekly": t_wk_all.to_dict("records")[0], "monthly": t_mo_all.to_dict("records")[0],
               "weekly_n_expiries": int(wk["expiry"].nunique()), "monthly_n_expiries": int(mo["expiry"].nunique()),
               "weekly_window": [str(wk["origin"].min()), str(wk["expiry"].max())],
               "straddle": so_tab.to_dict("records"), "example_reel1": ex1, "example_reel2": ex2}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    write_md(summary, t_wk_all, t_wk_dte, t_mo_all, t_mo_b, cal_wk, cal_wk5, cal_mo, yearly, so_tab, wk)
    import importlib.util
    spec = importlib.util.spec_from_file_location("em_charts", HERE / "charts.py")
    ch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ch)
    wk_dte2 = wk[wk["dte"] == 2]
    reel1 = pd.DataFrame([
        ("VIX range, weekly expiry (all days)", 100 * wk["close_inside"].mean(), *cluster_ci(wk, "close_inside")),
        ("VIX range, 2 days to weekly expiry", 100 * wk_dte2["close_inside"].mean(),
         *wilson(int(wk_dte2["close_inside"].sum()), len(wk_dte2))),
        ("VIX range, monthly expiry", 100 * mo["close_inside"].mean(), *cluster_ci(mo, "close_inside")),
        ("Straddle x 1.25, weekly (2026 only)", 100 * so["straddle_close_inside"].mean(),
         *cluster_ci(so, "straddle_close_inside")),
        ("VIX range never left all week", 100 * wk["range_inside"].mean(), *cluster_ci(wk, "range_inside")),
    ], columns=["label", "actual", "ci_low", "ci_high"])
    reel1.to_csv(OUT / "reel1_summary.csv", index=False, float_format="%.2f")
    ch.summary_chart(reel1, cal_wk, wk, OUT / "chart_reels_test.png")
    w = summary["weekly"]
    print(f"weekly: {w['observations']} obs / {summary['weekly_n_expiries']} expiries, close inside 1-sd "
          f"{w['close_inside_%']:.1f}% (claim 68.3%), whole path inside {w['whole_path_inside_%']:.1f}%")


def write_md(s, t_wk_all, t_wk_dte, t_mo_all, t_mo_b, cal_wk, cal_wk5, cal_mo, yearly, so_tab, wk) -> None:
    e1, e2 = s["example_reel1"], s["example_reel2"]
    L = ["# Expected-move reels: results (generated by analyze.py)", "",
         f"Weekly expiries tested: {s['weekly_n_expiries']} ({s['weekly_window'][0]} to {s['weekly_window'][1]}); "
         f"monthly: {s['monthly_n_expiries']}. Expiry calendar checked against NSE F&O files: "
         f"{s['calendar_check']['weekly_expiries_matched']} weekly expiries in {s['calendar_check']['window'][0]} to "
         f"{s['calendar_check']['window'][1]} match exactly.", "",
         "## Reel 1 - VIX expected move: does NIFTY close inside Spot +/- EM at expiry 68% of the time?", "",
         "Weekly expiries, all origins pooled (95% CI resamples whole expiries):", "", md(t_wk_all), "",
         "By calendar days to expiry (DTE 2 = the reel's case; Wilson 95% CI):", "", md(t_wk_dte), "",
         "Monthly expiries:", "", md(t_mo_all), "", md(t_mo_b), "",
         "## Reel 1 - ATM straddle x 1.25 (official NSE option closes, 3 Aug - 13 Nov 2026)", "",
         "Range centred on the level implied by the option prices (put-call parity); outcome = official close "
         "at expiry (the options' settlement value).", "", md(so_tab), "",
         "## Reel 2 - probability calculator: claimed vs actual (weekly expiries, all DTE)", "", md(cal_wk, "{:,.2f}"), "",
         "Weekly, DTE = 5 only (the reel's example; Tuesday-expiry era):", "", md(cal_wk5, "{:,.2f}"), "",
         "Monthly expiries:", "", md(cal_mo, "{:,.2f}"), "",
         "## By year (weekly expiries, all DTE)", "", md(yearly, "{:,.2f}"), "",
         "## The reels' own examples", "",
         f"* Reel 1 (Fri 4 Sep 2026, NIFTY {e1['spot']:,.2f}, VIX {e1['vix']}): EM with 2 days = {e1['em_reel']:.2f} "
         f"(the reel's 188.9); with the 4 calendar days from Friday's close to Tuesday's expiry = "
         f"{e1['em_calendar_days_from_friday_close']:.2f}. End-of-day ATM straddle ({e1['atm_strike']:.0f}) "
         f"{e1['straddle_eod_atm']:.2f} -> x1.25 = {e1['em_straddle']:.2f} around {e1['center_parity']:,.2f}. "
         f"Expiry {e1['expiry']} close: {e1['close_at_expiry']:,.2f}.",
         f"* Reel 2 (VIX 19, 5 days): the quoted 93% / 96% imply spot {e2['implied_spot']:,.0f}; formula check: "
         f"P(below 24,500) = {100 * e2['p_below_24500']:.1f}%, P(above 22,800) = {100 * e2['p_above_22800']:.1f}%.", ""]
    (OUT / "RESULTS.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
