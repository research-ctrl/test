#!/usr/bin/env python3
"""
fetch_data.py - build the documented input dataset for the NIFTY 50 range-forecast backtest.

DATA
----
NSE publishes one official "daily index closing" report per trading session:

    https://nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv

Each file holds Open / High / Low / Close for every NSE index on that date, including
"Nifty 50" (the cash index - NOT futures) and "India VIX". Using this one official file
for both series guarantees that NIFTY and VIX are aligned to the same NSE session.

SOURCES (choose with --source)
------------------------------
  nse      Download every file directly from NSE (official, preferred).
  mirrors  Read byte-for-byte copies of the same official files from independent public
           GitHub archives that download them from NSE every day. This is what was used for
           the committed dataset, because NSE / niftyindices.com hosts were blocked by the
           network policy of the environment in which the backtest was run.
  local    Read ind_close_all files you downloaded yourself (any file names; the date is read
           from the "Index Date" column inside each file).

INTEGRITY CHECKS (all sources)
------------------------------
  * the "Index Date" inside every file must equal the date implied by its file name;
  * mirrors: copies of the same date held by different archives are compared byte-for-byte
    (git blob SHA-1). Where an archive holds an earlier/later revision of NSE's file, the
    Nifty 50 and India VIX rows must still be identical, otherwise the script stops;
  * the set of sessions must match NSE's official 2026 trading calendar
    (data/nse_trading_calendar_2026.json): no missing and no unexpected sessions;
  * continuity: Close[t] - Close[t-1] must equal the "Points Change" NSE reports in the
    file for day t (for Nifty 50 and India VIX). A skipped or duplicated session breaks this;
  * OHLC sanity: Low <= Open, Close <= High.
Nothing is estimated, interpolated or filled: a session without an official file is reported
as missing and left out of the dataset.

OUTPUTS
-------
  data/nifty50_india_vix_daily.csv      documented input used by backtest.py
  data/provenance_manifest.csv          every source file: archive, commit, path, hashes, rows
  data/data_verification_report.md      results of the integrity checks

USAGE
-----
  python fetch_data.py --source mirrors            # pinned archive commits (reproducible)
  python fetch_data.py --source mirrors --latest   # newest archive commits (picks up new days)
  python fetch_data.py --source nse                # direct from NSE (needs NSE access)
  python fetch_data.py --source local --local-dir ~/Downloads/nse_index_files
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
CALENDAR_FILE = DATA_DIR / "nse_trading_calendar_2026.json"

DEFAULT_START = dt.date(2026, 6, 1)
DEFAULT_END = dt.date(2026, 11, 17)

NSE_URL = "https://nsearchives.nseindia.com/content/indices/ind_close_all_{d:%d%m%Y}.csv"
TARGET_ROWS = {"NIFTY 50": "nifty", "INDIA VIX": "vix"}

# Independent public GitHub archives that save NSE's ind_close_all file unmodified.
# 'commit' pins the exact snapshot used for the committed dataset.
ARCHIVES = [
    dict(key="bhavcopy", repo="Chaudharyrohit2506/bhavcopy",
         commit="d321094580e9e4cc1ecdd831e3b2590b801dbf71",
         subdir="data/aux/indices", glob="*.csv",
         name_re=r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\.csv$"),
    dict(key="powernse", repo="inquilabee/powernse",
         commit="6d3211c7d456c6aa141dff949a5d61289a7d95b4",
         subdir="nse-data/raw/index_closes/2026", glob="*.csv",
         name_re=r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\.csv$"),
    dict(key="olo", repo="olo-labs/olo-ai-training-data-nse-day-index-candle",
         commit="d0db8b71ed905383f8df5d0436470f572739ff14",
         subdir="Day_Index/NSE", glob="ind_close_all_*2026.csv",
         name_re=r"^ind_close_all_(?P<d>\d{2})(?P<m>\d{2})(?P<y>\d{4})\.csv$"),
    dict(key="quantdata", repo="noswear94/quantdata",
         commit="9784ffe2e39e9dbd2a44559bf17af7aeee6dc441",
         subdir="raw/bhavcopy/index/2026", glob="*.csv",
         name_re=r"^ind_close_all_(?P<d>\d{2})(?P<m>\d{2})(?P<y>\d{4})\.csv$"),
    dict(key="groww", repo="sahilempire/groww-market-data",
         commit="7d481cf1fcffe44be68852892028195c4f12dddd",
         subdir="nse_archives/index_close", glob="ind_close_all_2026*.csv",
         name_re=r"^ind_close_all_(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2})\.csv$"),
]


# --------------------------------------------------------------------------- helpers
def git_blob_sha1(content: bytes) -> str:
    """SHA-1 exactly as git computes it for a file (lets us compare against git trees)."""
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def run(cmd: list[str], cwd: Path | None = None) -> str:
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout


def num(s: str | None) -> float | None:
    s = (s or "").strip().replace(",", "")
    if s in ("", "-"):
        return None
    return float(s)


def parse_index_file(content: bytes) -> dict:
    """Extract the Nifty 50 and India VIX rows from one ind_close_all file."""
    text = content.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    header = next(csv.reader([lines[0]]))
    out = {}
    for raw_line in lines[1:]:
        fields = next(csv.reader([raw_line]))
        row = dict(zip(header, fields))
        name = (row.get("Index Name") or "").strip().upper()
        if name not in TARGET_ROWS:
            continue
        if TARGET_ROWS[name] in out:
            raise ValueError(f"duplicate row for {name}")
        out[TARGET_ROWS[name]] = {
            "raw": raw_line.strip(),
            "index_date": dt.datetime.strptime(row["Index Date"].strip(), "%d-%m-%Y").date(),
            "open": num(row.get("Open Index Value")),
            "high": num(row.get("High Index Value")),
            "low": num(row.get("Low Index Value")),
            "close": num(row.get("Closing Index Value")),
            "points_change": num(row.get("Points Change")),
            "change_pct": num(row.get("Change(%)")),
        }
    missing = [k for k in TARGET_ROWS.values() if k not in out]
    if missing:
        raise ValueError(f"rows not found in file: {missing}")
    return out


def load_calendar() -> tuple[set[dt.date], dict[dt.date, str]]:
    cal = json.loads(CALENDAR_FILE.read_text())
    holidays = {dt.date.fromisoformat(d) for d in cal["holidays"]}
    special = {dt.date.fromisoformat(d): why for d, why in cal["special_sessions"].items()}
    return holidays, special


def expected_sessions(start: dt.date, end: dt.date) -> dict[dt.date, str]:
    holidays, special = load_calendar()
    out = {}
    d = start
    while d <= end:
        if d in special:
            out[d] = "special"
        elif d.weekday() < 5 and d not in holidays:
            out[d] = "regular"
        d += dt.timedelta(days=1)
    return out


# --------------------------------------------------------------------------- sources
def collect_mirrors(cache: Path, latest: bool, start: dt.date, end: dt.date) -> tuple[list, dict]:
    """Return [(date, source_key, meta, content)] from the public GitHub archives."""
    records, commits = [], {}
    for a in ARCHIVES:
        url = f"https://github.com/{a['repo']}"
        repo_dir = cache / a["repo"].lower()
        if not (repo_dir / ".git").exists():
            repo_dir.parent.mkdir(parents=True, exist_ok=True)
            print(f"  cloning {a['repo']} (trees only) ...")
            run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout",
                 url, str(repo_dir)])
        origin = run(["git", "-C", str(repo_dir), "remote", "get-url", "origin"]).strip()
        if origin.lower().rstrip("/").removesuffix(".git") != url.lower():
            raise RuntimeError(f"{repo_dir} is not a clone of {url} (origin={origin})")
        if latest:
            run(["git", "-C", str(repo_dir), "fetch", "-q", "--depth", "1", "origin"])
            commit = run(["git", "-C", str(repo_dir), "rev-parse", "FETCH_HEAD"]).strip()
        else:
            commit = a["commit"]
            have = subprocess.run(["git", "-C", str(repo_dir), "cat-file", "-e", f"{commit}^{{commit}}"],
                                  capture_output=True).returncode == 0
            if not have:
                run(["git", "-C", str(repo_dir), "fetch", "-q", "--depth", "1", "origin", commit])
        # sparse checkout of just the needed files: git batch-downloads only those blobs
        run(["git", "-C", str(repo_dir), "sparse-checkout", "set", "--no-cone",
             f"/{a['subdir']}/{a['glob']}"])
        run(["git", "-C", str(repo_dir), "checkout", "-q", "--detach", commit])
        commits[a["key"]] = dict(repo=a["repo"], url=url, commit=commit,
                                 commit_time=run(["git", "-C", str(repo_dir), "log", "-1",
                                                  "--format=%cI", commit]).strip())
        tree = run(["git", "-C", str(repo_dir), "ls-tree", "-r", commit, a["subdir"] + "/"])
        n = 0
        for line in tree.splitlines():
            meta, path = line.split("\t", 1)
            blob = meta.split()[2]
            m = re.match(a["name_re"], Path(path).name)
            if not m:
                continue
            date = dt.date(int(m["y"]), int(m["m"]), int(m["d"]))
            if not (start <= date <= end):
                continue
            content = (repo_dir / path).read_bytes()
            if git_blob_sha1(content) != blob:
                raise RuntimeError(f"working-tree file differs from git tree: {a['repo']}:{path}")
            records.append((date, a["key"], dict(repo=a["repo"], commit=commit, path=path,
                                                 url=f"{url}/blob/{commit}/{path}"), content))
            n += 1
        print(f"  {a['repo']}@{commit[:10]}: {n} files in range")
    return records, commits


def collect_nse(start: dt.date, end: dt.date, raw_dir: Path) -> tuple[list, dict]:
    """Download the official files directly from NSE (requires access to nseindia.com)."""
    import requests  # imported here so the mirror/local modes need no third-party package

    raw_dir.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                    "(KHTML, like Gecko) Chrome/131 Safari/537.36",
                      "Accept": "*/*", "Referer": "https://www.nseindia.com/"})
    try:
        s.get("https://www.nseindia.com/", timeout=20)  # obtain cookies
    except Exception as exc:  # noqa: BLE001
        print("  warning: NSE home page not reachable:", exc)
    records = []
    for d in expected_sessions(start, end):
        url = NSE_URL.format(d=d)
        out = raw_dir / f"ind_close_all_{d:%d%m%Y}.csv"
        if not out.exists():
            r = s.get(url, timeout=45)
            if r.status_code != 200 or len(r.content) < 1000:
                print(f"  {d}: not available from NSE (HTTP {r.status_code})")
                continue
            out.write_bytes(r.content)
            time.sleep(0.3)
        records.append((d, "nse_direct", dict(repo="nseindia.com", commit="", path=str(out),
                                              url=url), out.read_bytes()))
    return records, {"nse_direct": dict(repo="nseindia.com", url="https://www.nseindia.com",
                                        commit="", commit_time=dt.datetime.now().isoformat())}


def collect_local(local_dir: Path, start: dt.date, end: dt.date) -> tuple[list, dict]:
    records = []
    for p in sorted(local_dir.glob("*.csv")):
        content = p.read_bytes()
        try:
            date = parse_index_file(content)["nifty"]["index_date"]
        except Exception:  # noqa: BLE001 - not an ind_close_all file
            continue
        if start <= date <= end:
            records.append((date, "local", dict(repo=str(local_dir), commit="", path=p.name,
                                                url=NSE_URL.format(d=date)), content))
    return records, {"local": dict(repo=str(local_dir), url="", commit="", commit_time="")}


# --------------------------------------------------------------------------- build + verify
def build(records: list, commits: dict, start: dt.date, end: dt.date, source: str) -> None:
    expected = expected_sessions(start, end)
    by_date: dict[dt.date, list] = defaultdict(list)
    manifest_rows, problems, notes = [], [], []

    for date, key, meta, content in records:
        parsed = parse_index_file(content)
        for k in ("nifty", "vix"):
            if parsed[k]["index_date"] != date:
                problems.append(f"{date} {key}: file name date != Index Date {parsed[k]['index_date']}")
        by_date[date].append((key, meta, content, parsed))
        manifest_rows.append({
            "date": date.isoformat(), "archive": key, "repo": meta["repo"], "commit": meta["commit"],
            "path": meta["path"], "source_url": meta["url"], "nse_official_url": NSE_URL.format(d=date),
            "bytes": len(content), "git_blob_sha1": git_blob_sha1(content), "sha256": sha256(content),
            "nifty50_row": parsed["nifty"]["raw"], "india_vix_row": parsed["vix"]["raw"],
        })

    unexpected = sorted(d for d in by_date if d not in expected)
    for d in unexpected:
        problems.append(f"{d}: file present but date is not an NSE session per the official calendar")
    missing = sorted(d for d in expected if d not in by_date)

    dataset, multi, single, revisions = [], 0, [], []
    for date in sorted(d for d in by_date if d in expected):
        copies = by_date[date]
        blobs = Counter(git_blob_sha1(c[2]) for c in copies)
        nifty_rows = {c[3]["nifty"]["raw"] for c in copies}
        vix_rows = {c[3]["vix"]["raw"] for c in copies}
        if len(nifty_rows) > 1 or len(vix_rows) > 1:
            raise SystemExit(f"CONFLICT on {date}: archives disagree on Nifty 50 / India VIX rows:\n"
                             f"{nifty_rows}\n{vix_rows}")
        if len(copies) >= 2:
            multi += 1
        else:
            single.append(date)
        if len(blobs) > 1:
            revisions.append(date)
            note = (f"{len(blobs)} revisions of NSE's file across archives (later revision adds other "
                    f"indices); Nifty 50 and India VIX rows identical in all {len(copies)} copies")
        elif len(copies) >= 2:
            note = f"byte-identical in all {len(copies)} archives"
        else:
            note = "single archive copy"
        p = copies[0][3]
        n, v = p["nifty"], p["vix"]
        dataset.append({
            "date": date.isoformat(), "weekday": date.strftime("%a"),
            "session_type": "regular" if expected[date] == "regular" else "muhurat_special",
            "nifty_open": n["open"], "nifty_high": n["high"], "nifty_low": n["low"], "nifty_close": n["close"],
            "nifty_points_change": n["points_change"], "nifty_change_pct": n["change_pct"],
            "vix_open": v["open"], "vix_high": v["high"], "vix_low": v["low"], "vix_close": v["close"],
            "vix_points_change": v["points_change"], "vix_change_pct": v["change_pct"],
            "n_copies": len(copies), "archives": "|".join(sorted(c[0] for c in copies)),
            "file_git_blob_sha1": "|".join(b for b, _ in blobs.most_common()),
            "verification": note, "nse_official_url": NSE_URL.format(d=date),
        })

    # continuity + OHLC sanity on the full official series (incl. special sessions)
    continuity_fail = []
    for i, row in enumerate(dataset):
        for pre in ("nifty", "vix"):
            o, h, l, c = (row[f"{pre}_{k}"] for k in ("open", "high", "low", "close"))
            if not (l <= min(o, c) and max(o, c) <= h):
                problems.append(f"{row['date']} {pre}: OHLC inconsistent ({o},{h},{l},{c})")
            if i > 0:
                implied = round(c - dataset[i - 1][f"{pre}_close"], 4)
                if abs(implied - row[f"{pre}_points_change"]) > 0.011:
                    continuity_fail.append(f"{row['date']} {pre}: close diff {implied} vs NSE points change "
                                           f"{row[f'{pre}_points_change']} (previous file {dataset[i-1]['date']})")
    problems += continuity_fail

    DATA_DIR.mkdir(exist_ok=True)
    out_csv = DATA_DIR / "nifty50_india_vix_daily.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dataset[0].keys()))
        w.writeheader()
        w.writerows(dataset)
    with (DATA_DIR / "provenance_manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(manifest_rows, key=lambda r: (r["date"], r["archive"])))

    first = dataset[0]
    lines = [
        "# Data verification report",
        "",
        f"Generated by `fetch_data.py --source {source}` on {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC.",
        "",
        "Every row of `nifty50_india_vix_daily.csv` comes from NSE's official daily index closing report "
        "`ind_close_all_DDMMYYYY.csv` (official URL pattern: "
        "`https://nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv`).",
        "",
        "## Sources and snapshots",
        "",
        "| Source | Snapshot (commit) | Commit time |",
        "|---|---|---|",
    ]
    for k, c in commits.items():
        lines.append(f"| {c['url'] or c['repo']} | `{c['commit']}` | {c['commit_time']} |")
    lines += [
        "",
        "## Results",
        "",
        f"* Requested range: {start} to {end}. NSE sessions in range per official calendar: **{len(expected)}** "
        f"({sum(1 for t in expected.values() if t == 'regular')} regular + "
        f"{sum(1 for t in expected.values() if t != 'regular')} special).",
        f"* Sessions with an official file: **{len(dataset)}**. Missing: **{len(missing)}** "
        f"{'(' + ', '.join(map(str, missing)) + ')' if missing else ''}.",
        f"* Sessions held by >= 2 independent archives: **{multi}**; all copies byte-identical on "
        f"**{multi - len([d for d in revisions if d not in single])}** of them.",
        f"* Dates where archives hold different revisions of NSE's file: "
        f"{', '.join(map(str, revisions)) or 'none'} - Nifty 50 and India VIX rows identical in every copy "
        "(the later revision only adds rows for other indices).",
        f"* Single-copy dates: {', '.join(map(str, single)) or 'none'} - validated by the continuity check below.",
        f"* Continuity check (Close[t] - Close[t-1] == NSE 'Points Change'[t], Nifty 50 and India VIX): "
        f"**{'PASS' if not continuity_fail else 'FAIL'}** on {len(dataset) - 1} consecutive pairs.",
        f"* Unexpected files on non-session dates: {', '.join(map(str, unexpected)) or 'none'}.",
        f"* First session {first['date']}: NSE-reported previous close "
        f"{round(first['nifty_close'] - first['nifty_points_change'], 2)} (Close - Points Change).",
        "",
        "## Problems",
        "",
    ]
    lines += [f"* {p}" for p in problems] or ["None."]
    if missing:
        lines += ["", "## Missing sessions (NOT filled or estimated)", ""]
        lines += [f"* {d} ({d:%a}): no official file available from the selected source at run time."
                  for d in missing]
    (DATA_DIR / "data_verification_report.md").write_text("\n".join(lines) + "\n")

    print(f"\n  sessions expected {len(expected)}, built {len(dataset)}, missing {missing or 'none'}")
    print(f"  multi-archive {multi}, revisions {revisions or 'none'}, single-copy {single or 'none'}")
    print(f"  continuity {'PASS' if not continuity_fail else 'FAIL'}; problems: {len(problems)}")
    for p in problems:
        print("   -", p)
    print(f"  wrote {out_csv.relative_to(HERE)}, provenance_manifest.csv, data_verification_report.md")
    if problems:
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=["mirrors", "nse", "local"], default="mirrors")
    ap.add_argument("--latest", action="store_true", help="mirrors: use newest archive commits instead of pins")
    ap.add_argument("--cache-dir", type=Path, default=HERE / ".cache" / "archives",
                    help="mirrors: where archive clones are kept (default: .cache/archives)")
    ap.add_argument("--local-dir", type=Path, help="local: folder containing ind_close_all CSV files")
    ap.add_argument("--start", type=dt.date.fromisoformat, default=DEFAULT_START)
    ap.add_argument("--end", type=dt.date.fromisoformat, default=DEFAULT_END)
    args = ap.parse_args()

    print(f"source={args.source} range={args.start}..{args.end}")
    if args.source == "mirrors":
        records, commits = collect_mirrors(args.cache_dir, args.latest, args.start, args.end)
    elif args.source == "nse":
        records, commits = collect_nse(args.start, args.end, DATA_DIR / "raw_nse")
    else:
        if not args.local_dir:
            ap.error("--local-dir is required with --source local")
        records, commits = collect_local(args.local_dir, args.start, args.end)
    if not records:
        raise SystemExit("no files collected")
    build(records, commits, args.start, args.end, args.source)


if __name__ == "__main__":
    main()
