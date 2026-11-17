# History verification (2019-2026)

* Sessions: 1946 (2019-01-01 to 2026-11-16); held by >= 2 independent archives: 1938; byte-identical in all copies: 1552 of those.
* Single-copy sessions: 2021-11-04, 2022-10-24, 2024-01-20, 2024-11-01, 2025-02-01, 2025-10-21, 2026-11-08, 2026-11-16.
* Continuity (Close[t] - Close[t-1] == NSE Points Change[t], Nifty 50 and India VIX) and OHLC sanity: **PASS** on 1945 consecutive pairs.
* Special (short) sessions flagged and excluded from the analysis: 2021-11-04 (Thu), 2022-10-24 (Mon), 2024-01-20 (Sat), 2024-11-01 (Fri), 2025-02-01 (Sat), 2025-10-21 (Tue), 2026-11-08 (Sun).
* Internal 'Index Date' format used by NSE in the files (always checked against the file date): %d-%m-%Y: 1943, %m-%d-%Y: 3.
* Rows published by NSE without Open/High/Low (close repeated from the previous day; these days are not used as forecast origins): 2021-02-12 vix: NSE row has no Open/High/Low (`India VIX,12-02-2021,-,-,-,23.05,0.0,0,-,-,-,-,-`); 2021-03-30 vix: NSE row has no Open/High/Low (`India VIX,30-03-2021,-,-,-,20.65,0.0,0,-,-,-,-,-`).

## Continuity breaks with a checked explanation (not missing trading days)

* 2019-10-29: change measured from 2019-10-27, Diwali Muhurat trading (Sun), a session the archives do not store
* 2020-02-03: change measured from 2020-02-01, Union Budget special session (Sat), a session the archives do not store
* 2020-11-17: change measured from 2020-11-14, Diwali Muhurat trading (Sat), a session the archives do not store
* 2023-03-13: NSE's file measures Points Change from 2023-03-09 instead of 2023-03-10 (verified for Nifty 50 and India VIX; 2023-03-10's own change is consistent)
* 2023-11-13: change measured from 2023-11-12, Diwali Muhurat trading (Sun), a session the archives do not store
* 2024-03-04: change measured from 2024-03-02, special live session from the disaster-recovery site (Sat), a session the archives do not store
* 2024-05-21: change measured from 2024-05-18, special live session from the disaster-recovery site (Sat), a session the archives do not store
* 2026-02-02: change measured from 2026-02-01, Union Budget special session (Sun), a session the archives do not store

## Problems

None.
