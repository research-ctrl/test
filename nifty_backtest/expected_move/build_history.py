#!/usr/bin/env python3
"""
build_history.py - inputs for testing the two "expected move" reels.

1. NIFTY 50 + India VIX daily history, Jan 2019 - Nov 2026, from NSE's official daily index
   closing reports (ind_close_all), read from independent public archives that store them
   unmodified (same archives as ../fetch_data.py). Checks: cross-archive agreement of the
   Nifty 50 / India VIX rows (byte-identical files in almost all cases), NSE "Points Change"
   continuity on every consecutive pair of sessions (proves no session is missing), OHLC sanity.
   Short special sessions (weekend sessions, Diwali Muhurat) are flagged so that they are
   never treated as normal trading days or expiries.

2. NIFTY at-the-money straddle at each day's close, 3 Aug - 13 Nov 2026, from NSE's official
   F&O bhavcopy (BhavCopy_NSE_FO_*.csv, as archived by inquilabee/powernse), plus every NIFTY
   option expiry date listed in those files (used to verify the expiry calendar).

Outputs (data/):  nifty_vix_daily_2019_2026.csv, history_provenance.csv,
                  history_verification.md, nifty_atm_straddle_2026.csv, nifty_option_expiries_2026.csv
Usage:  python build_history.py [--cache-dir DIR]   (DIR holds/receives the archive clones)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import json
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
_spec = importlib.util.spec_from_file_location("fetch_data", HERE.parent / "fetch_data.py")
fd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fd)

START, END = dt.date(2019, 1, 1), dt.date(2026, 11, 17)
YEARS = range(START.year, END.year + 1)
ARCHIVES = [
    dict(key="powernse", repo="inquilabee/powernse", commit="6d3211c7d456c6aa141dff949a5d61289a7d95b4",
         subdir="nse-data/raw/index_closes", globs=[f"{y}/*.csv" for y in YEARS],
         name_re=r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\.csv$"),
    dict(key="olo", repo="olo-labs/olo-ai-training-data-nse-day-index-candle",
         commit="d0db8b71ed905383f8df5d0436470f572739ff14", subdir="Day_Index/NSE",
         globs=[f"ind_close_all_*{y}.csv" for y in YEARS],
         name_re=r"^ind_close_all_(?P<d>\d{2})(?P<m>\d{2})(?P<y>\d{4})\.csv$"),
    dict(key="bhavcopy", repo="Chaudharyrohit2506/bhavcopy", commit="d321094580e9e4cc1ecdd831e3b2590b801dbf71",
         subdir="data/aux/indices", globs=["*.csv"], name_re=r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\.csv$"),
]
FO = dict(repo="inquilabee/powernse", commit="6d3211c7d456c6aa141dff949a5d61289a7d95b4",
          subdir="nse-data/raw/fo_bhavcopy/2026", manifest="nse-data/manifest/downloads.jsonl")
LOW_VOLUME_RATIO = 0.35  # weekday session with < 35% of the local median Nifty 50 volume = special (Muhurat)


def checkout(repo: str, commit: str, patterns: list[str], cache: Path) -> Path:
    url = f"https://github.com/{repo}"
    d = cache / repo.lower()
    if not (d / ".git").exists():
        d.parent.mkdir(parents=True, exist_ok=True)
        fd.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", url, str(d)])
    have = subprocess.run(["git", "-C", str(d), "cat-file", "-e", f"{commit}^{{commit}}"],
                          capture_output=True).returncode == 0
    if not have:
        fd.run(["git", "-C", str(d), "fetch", "-q", "--depth", "1", "origin", commit])
    fd.run(["git", "-C", str(d), "sparse-checkout", "set", "--no-cone", *patterns])
    fd.run(["git", "-C", str(d), "checkout", "-q", "--detach", commit])
    return d


def tree(d: Path, commit: str, sub: str) -> list[tuple[str, str]]:
    out = fd.run(["git", "-C", str(d), "ls-tree", "-r", commit, sub.rstrip("/") + "/"])
    return [(ln.split("\t", 1)[1], ln.split()[2]) for ln in out.splitlines()]


DATE_FORMATS = ("%d-%m-%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y")


def parse_file(content: bytes) -> dict:
    """Nifty 50 and India VIX rows of one ind_close_all file. NSE has used both DD-MM-YYYY and
    MM-DD-YYYY inside these files, so the raw date string is kept and checked against the file
    date separately (see date_format)."""
    lines = [ln for ln in content.decode("utf-8-sig").splitlines() if ln.strip()]
    header = [h.strip() for h in next(csv.reader([lines[0]]))]
    out = {}
    for raw in lines[1:]:
        row = dict(zip(header, next(csv.reader([raw]))))
        key = {"NIFTY 50": "nifty", "INDIA VIX": "vix"}.get((row.get("Index Name") or "").strip().upper())
        if key is None:
            continue
        if key in out:
            raise ValueError(f"duplicate {key} row")
        out[key] = {"raw": raw.strip(), "date_raw": row["Index Date"].strip(),
                    "open": fd.num(row["Open Index Value"]), "high": fd.num(row["High Index Value"]),
                    "low": fd.num(row["Low Index Value"]), "close": fd.num(row["Closing Index Value"]),
                    "points_change": fd.num(row["Points Change"]), "volume": fd.num(row.get("Volume"))}
    if set(out) != {"nifty", "vix"}:
        raise ValueError(f"rows found: {sorted(out)}")
    return out


def date_format(raw: str, date: dt.date) -> str | None:
    """Return the format under which the file's internal date equals its file-name date, else None."""
    for f in DATE_FORMATS:
        try:
            if dt.datetime.strptime(raw, f).date() == date:
                return f
        except ValueError:
            pass
    return None


def build_index_history(cache: Path) -> dict[dt.date, dict]:
    copies: dict[dt.date, list] = defaultdict(list)
    prov = []
    for a in ARCHIVES:
        d = checkout(a["repo"], a["commit"], [f"/{a['subdir']}/{g}" for g in a["globs"]], cache)
        n = 0
        for path, blob in tree(d, a["commit"], a["subdir"]):
            m = re.match(a["name_re"], Path(path).name)
            if not m:
                continue
            date = dt.date(int(m["y"]), int(m["m"]), int(m["d"]))
            if not (START <= date <= END):
                continue
            content = (d / path).read_bytes()
            if fd.git_blob_sha1(content) != blob:
                raise RuntimeError(f"working tree differs from git tree: {a['repo']}:{path}")
            parsed = parse_file(content)
            fmts = {date_format(parsed[k]["date_raw"], date) for k in ("nifty", "vix")}
            if None in fmts:
                raise RuntimeError(f"{a['repo']}:{path}: internal date {parsed['nifty']['date_raw']} "
                                   f"does not match file date {date} in any known format")
            parsed["date_format"] = "|".join(sorted(fmts))
            copies[date].append((a["key"], parsed, blob, parsed["nifty"]["volume"]))
            prov.append({"date": date.isoformat(), "archive": a["key"], "repo": a["repo"], "commit": a["commit"],
                         "path": path, "git_blob_sha1": blob, "nifty50_row": parsed["nifty"]["raw"],
                         "india_vix_row": parsed["vix"]["raw"]})
            n += 1
        print(f"  {a['repo']}@{a['commit'][:10]}: {n} files in {START}..{END}")
    with (DATA / "history_provenance.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(prov[0]))
        w.writeheader()
        w.writerows(sorted(prov, key=lambda r: (r["date"], r["archive"])))
    hist = {}
    for date in sorted(copies):
        c = copies[date]
        if len({x[1]["nifty"]["raw"] for x in c}) > 1 or len({x[1]["vix"]["raw"] for x in c}) > 1:
            raise SystemExit(f"CONFLICT {date}: archives disagree on Nifty 50 / India VIX rows")
        p = c[0][1]
        hist[date] = {"nifty": p["nifty"], "vix": p["vix"], "volume": c[0][3], "n_copies": len(c),
                      "archives": "|".join(sorted(x[0] for x in c)),
                      "identical_bytes": len({x[2] for x in c}) == 1, "date_format": p["date_format"]}
    return hist


INCOMPLETE: list[str] = []  # rows where NSE published no Open/High/Low (close carried forward by NSE)
EXPLAINED: list[str] = []    # continuity breaks with a documented, checked explanation
# Weekend special sessions held by NSE but not stored by the archives (their downloaders skip weekends).
# NSE's "Points Change" on the next trading day is measured from these sessions, so continuity breaks there.
KNOWN_SPECIAL_SESSIONS = {
    dt.date(2019, 10, 27): "Diwali Muhurat trading (Sun)",
    dt.date(2020, 2, 1): "Union Budget special session (Sat)",
    dt.date(2020, 11, 14): "Diwali Muhurat trading (Sat)",
    dt.date(2023, 11, 12): "Diwali Muhurat trading (Sun)",
    dt.date(2024, 3, 2): "special live session from the disaster-recovery site (Sat)",
    dt.date(2024, 5, 18): "special live session from the disaster-recovery site (Sat)",
    dt.date(2026, 2, 1): "Union Budget special session (Sun)",
}


def verify_and_flag(hist: dict[dt.date, dict]) -> tuple[list[str], list[dt.date]]:
    dates = sorted(hist)
    problems = []
    for i, d in enumerate(dates):
        for k in ("nifty", "vix"):
            r = hist[d][k]
            if None in (r["open"], r["high"], r["low"]):
                INCOMPLETE.append(f"{d} {k}: NSE row has no Open/High/Low (`{r['raw']}`)")
            elif not (r["low"] <= min(r["open"], r["close"]) and max(r["open"], r["close"]) <= r["high"]):
                problems.append(f"{d} {k}: OHLC inconsistent")
        if i:
            p = dates[i - 1]
            breaks = [k for k in ("nifty", "vix")
                      if abs(round(hist[d][k]["close"] - hist[p][k]["close"], 4) - hist[d][k]["points_change"]) > 0.011]
            if breaks:
                two_back = dates[i - 2] if i >= 2 else None
                quirk = two_back and all(
                    abs(round(hist[d][k]["close"] - hist[two_back][k]["close"], 4) - hist[d][k]["points_change"]) <= 0.011
                    for k in ("nifty", "vix"))
                gap_special = [s for s in KNOWN_SPECIAL_SESSIONS if p < s < d]
                if quirk:
                    EXPLAINED.append(f"{d}: NSE's file measures Points Change from {two_back} instead of {p} "
                                     f"(verified for Nifty 50 and India VIX; {p}'s own change is consistent)")
                elif gap_special:
                    s = gap_special[0]
                    EXPLAINED.append(f"{d}: change measured from {s}, {KNOWN_SPECIAL_SESSIONS[s]}, "
                                     "a session the archives do not store")
                else:
                    problems.append(f"{d} {'/'.join(breaks)}: close change != NSE points change (previous file {p})")
    special = []
    for i, d in enumerate(dates):
        if d.weekday() >= 5:
            special.append(d)
            continue
        window = [hist[x]["volume"] for x in dates[max(0, i - 10):i + 11] if x != d and x.weekday() < 5]
        if hist[d]["volume"] and hist[d]["volume"] < LOW_VOLUME_RATIO * statistics.median(window):
            special.append(d)
    return problems, special


def build_options(cache: Path, hist: dict[dt.date, dict]) -> None:
    d = checkout(FO["repo"], FO["commit"], [f"/{FO['subdir']}/*.csv", f"/{FO['manifest']}"], cache)
    urls = {}
    for line in (d / FO["manifest"]).read_text().splitlines():
        rec = json.loads(line)
        if "fo_bhavcopy" in rec.get("local_path", ""):
            urls[Path(rec["local_path"]).name] = (rec["url"], rec.get("sha256", ""))
    rows_out, expiries = [], defaultdict(set)
    for path, blob in tree(d, FO["commit"], FO["subdir"]):
        name = Path(path).name
        date = dt.date.fromisoformat(name[:10])
        content = (d / path).read_bytes()
        if fd.git_blob_sha1(content) != blob:
            raise RuntimeError(f"working tree differs from git tree: {path}")
        opts = [r for r in csv.DictReader(content.decode("utf-8-sig").splitlines())
                if r["TckrSymb"] == "NIFTY" and r["FinInstrmTp"] == "IDO"]
        if not opts or date not in hist:
            continue
        for r in opts:
            expiries[dt.date.fromisoformat(r["XpryDt"])].add(date)
        spot = hist[date]["nifty"]["close"]
        und = {float(r["UndrlygPric"]) for r in opts}
        nxt = min(e for e in {dt.date.fromisoformat(r["XpryDt"]) for r in opts} if e > date)
        chain = [r for r in opts if dt.date.fromisoformat(r["XpryDt"]) == nxt]
        legs: dict[float, dict] = defaultdict(dict)
        for r in chain:
            legs[float(r["StrkPric"])][r["OptnTp"]] = r
        # The official index close is built from the last-30-minute average prices of its stocks, whereas
        # option closes are 15:30 last-traded prices. The level the option prices actually refer to is
        # recovered by put-call parity (C - P + K = forward), median over strikes within 300 points.
        par = [k + float(v["CE"]["ClsPric"]) - float(v["PE"]["ClsPric"]) for k, v in legs.items()
               if "CE" in v and "PE" in v and abs(k - spot) <= 300]
        fwd = statistics.median(par)

        def straddle_at(level: float) -> tuple[float, float, float, dict, dict]:
            k = min((s for s, v in legs.items() if "CE" in v and "PE" in v), key=lambda s: (abs(s - level), s))
            ce, pe = legs[k]["CE"], legs[k]["PE"]
            return k, float(ce["ClsPric"]), float(pe["ClsPric"]), ce, pe

        k, cep, pep, ce, pe = straddle_at(fwd)
        k2, cep2, pep2, _, _ = straddle_at(spot)
        url, zsha = urls.get(name, ("", ""))
        rows_out.append({
            "date": date.isoformat(), "nifty_close": spot, "underlying_in_file": "|".join(f"{u:.2f}" for u in sorted(und)),
            "parity_implied_level": round(fwd, 2), "expiry": nxt.isoformat(), "dte_calendar": (nxt - date).days,
            "atm_strike": k, "ce_close": cep, "pe_close": pep, "straddle_close": round(cep + pep, 2),
            "ce_volume": int(float(ce["TtlTradgVol"])), "pe_volume": int(float(pe["TtlTradgVol"])),
            "strike_nearest_official_close": k2, "straddle_at_that_strike": round(cep2 + pep2, 2),
            "fo_file_git_blob_sha1": blob, "nse_official_url": url, "nse_zip_sha256": zsha,
        })
    with (DATA / "nifty_atm_straddle_2026.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0]))
        w.writeheader()
        w.writerows(sorted(rows_out, key=lambda r: r["date"]))
    with (DATA / "nifty_option_expiries_2026.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["expiry", "first_seen", "last_seen", "days_listed"])
        for e in sorted(expiries):
            w.writerow([e.isoformat(), min(expiries[e]).isoformat(), max(expiries[e]).isoformat(), len(expiries[e])])
    print(f"  F&O bhavcopy: {len(rows_out)} trading days of NIFTY ATM straddles; {len(expiries)} expiries listed")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", type=Path, default=HERE.parent / ".cache" / "archives")
    args = ap.parse_args()
    DATA.mkdir(exist_ok=True)
    hist = build_index_history(args.cache_dir)
    problems, special = verify_and_flag(hist)
    with (DATA / "nifty_vix_daily_2019_2026.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "weekday", "session_type", "nifty_open", "nifty_high", "nifty_low", "nifty_close",
                    "nifty_points_change", "nifty_volume", "vix_open", "vix_high", "vix_low", "vix_close",
                    "vix_points_change", "n_copies", "archives", "copies_byte_identical", "nse_internal_date_format"])
        for d in sorted(hist):
            n, v = hist[d]["nifty"], hist[d]["vix"]
            w.writerow([d.isoformat(), d.strftime("%a"), "special" if d in special else "regular",
                        n["open"], n["high"], n["low"], n["close"], n["points_change"], hist[d]["volume"],
                        v["open"], v["high"], v["low"], v["close"], v["points_change"],
                        hist[d]["n_copies"], hist[d]["archives"], hist[d]["identical_bytes"], hist[d]["date_format"]])
    multi = [d for d in hist if hist[d]["n_copies"] >= 2]
    fmt_counts = Counter(hist[d]["date_format"] for d in hist)
    lines = ["# History verification (2019-2026)", "",
             f"* Sessions: {len(hist)} ({min(hist)} to {max(hist)}); held by >= 2 independent archives: {len(multi)}; "
             f"byte-identical in all copies: {sum(hist[d]['identical_bytes'] for d in multi)} of those.",
             f"* Single-copy sessions: {', '.join(str(d) for d in sorted(hist) if hist[d]['n_copies'] == 1) or 'none'}.",
             f"* Continuity (Close[t] - Close[t-1] == NSE Points Change[t], Nifty 50 and India VIX) and OHLC "
             f"sanity: **{'PASS' if not problems else 'FAIL'}** on {len(hist) - 1} consecutive pairs.",
             f"* Special (short) sessions flagged and excluded from the analysis: "
             f"{', '.join(f'{d} ({d:%a})' for d in special)}.",
             f"* Internal 'Index Date' format used by NSE in the files (always checked against the file date): "
             f"{', '.join(f'{k}: {v}' for k, v in fmt_counts.most_common())}.",
             "* Rows published by NSE without Open/High/Low (close repeated from the previous day; these days "
             "are not used as forecast origins): " + ("; ".join(INCOMPLETE) or "none") + ".",
             "", "## Continuity breaks with a checked explanation (not missing trading days)", ""]
    lines += [f"* {e}" for e in EXPLAINED] or ["None."]
    lines += ["", "## Problems", ""]
    lines += [f"* {p}" for p in problems] or ["None."]
    (DATA / "history_verification.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:6]))
    if problems:
        raise SystemExit("verification failed")
    build_options(args.cache_dir, hist)


if __name__ == "__main__":
    main()
