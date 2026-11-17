"""Chart for analyze.py (static PNG, light theme; palette validated: blue #2a78d6 / orange #eb6834)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": SURFACE})


def _style(ax, grid_axis="both"):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8, length=0, pad=4)


def summary_chart(reel1: pd.DataFrame, cal_wk: pd.DataFrame, wk: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.6), gridspec_kw={"wspace": 0.42, "width_ratios": [1.25, 1, 1]})

    # 1. Reel 1: claimed 68% vs measured containment
    ax = axes[0]
    _style(ax, "x")
    y = np.arange(len(reel1))[::-1]
    ax.axvline(68.3, color=MUTED, lw=1.2, zorder=1)
    ax.text(68.3, len(reel1) - 0.35, "reel's claim 68%", color=INK2, fontsize=7.5, ha="center", va="bottom")
    for yi, r in zip(y, reel1.itertuples(index=False)):
        ax.hlines(yi, r.ci_low, r.ci_high, color=BLUE, lw=2, alpha=0.45, zorder=2)
        ax.plot(r.actual, yi, "o", ms=8, color=BLUE, mec=SURFACE, mew=1.5, zorder=3)
        ax.annotate(f"{r.actual:.1f}%", (r.ci_high, yi), xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(reel1["label"], fontsize=8, color=INK)
    ax.set_xlim(30, 100)
    ax.set_ylim(-0.6, len(reel1) - 0.1)
    ax.set_xlabel("NIFTY finished inside the range (%)  - dot = measured, bar = 95% CI", color=INK2)
    ax.set_title("Reel 1: 'closes inside the expected move 68% of the time'", loc="left", color=INK, fontsize=10)

    # 2. Reel 2: claimed vs actual breach rates at the 'safe' strikes
    ax = axes[1]
    _style(ax)
    t = cal_wk[cal_wk["model_probability_%"] >= 90].copy()
    claimed = 100 - t["model_probability_%"]
    ax.plot([0, 11], [0, 11], color=MUTED, lw=1.2, zorder=1)
    ax.text(10.6, 9.7, "claimed", color=INK2, fontsize=7.5, ha="right")
    series = [(100 - t["upside_close_below_strike_%"], BLUE, True, "Call strike: closed above it at expiry"),
              (100 - t["upside_never_traded_above_%"], BLUE, False, "Call strike: traded above it before expiry"),
              (100 - t["downside_close_above_strike_%"], ORANGE, True, "Put strike: closed below it at expiry"),
              (100 - t["downside_never_traded_below_%"], ORANGE, False, "Put strike: traded below it before expiry")]
    for vals, color, filled, label in series:
        ax.plot(claimed, vals, color=color, lw=2 if filled else 1.4, marker="o", ms=7,
                mfc=color if filled else SURFACE, mec=color, mew=1.6, label=label, zorder=3)
    r93 = t[t["model_probability_%"] == 93].iloc[0]
    ax.annotate(f"'93% safe' put strike:\ntouched in {100 - r93['downside_never_traded_below_%']:.1f}% of weeks",
                (7, 100 - r93["downside_never_traded_below_%"]), xytext=(7.4, 3.2), textcoords="data",
                fontsize=7.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, max(16, float(max(v.max() for v, *_ in series)) + 2))
    ax.set_xticks(claimed)
    ax.set_xticklabels([f"{c:.0f}%" for c in claimed], fontsize=8)
    ax.set_xlabel("Breach probability claimed (7% = the reel's '93% safe' strike)", color=INK2)
    ax.set_ylabel("Actual breach rate (%)", color=INK2)
    ax.legend(loc="upper left", frameon=False, fontsize=7.5, labelcolor=INK)
    ax.set_title("Reel 2: how often the 'safe' strike was breached", loc="left", color=INK, fontsize=10)

    # 3. Distribution of outcomes vs the bell curve
    ax = axes[2]
    _style(ax)
    z = wk["z"].clip(-6, 6)
    ax.hist(z, bins=np.arange(-6, 6.01, 0.25), density=True, color=BLUE, alpha=0.35, label="Actual outcomes")
    g = np.linspace(-6, 6, 400)
    ax.plot(g, np.exp(-g * g / 2) / np.sqrt(2 * np.pi), color=INK, lw=2, label="Bell curve the reels assume")
    ax.set_xlim(-6, 6)
    ax.set_xlabel("Move to expiry, in VIX-implied standard deviations", color=INK2)
    ax.set_ylabel("Density", color=INK2)
    ax.legend(loc="upper left", frameon=False, fontsize=8, labelcolor=INK)
    ax.set_title(f"Weekly outcomes vs the assumed bell curve (n = {len(wk):,})", loc="left", color=INK, fontsize=10)

    fig.suptitle("Testing two option-writing reels on real NIFTY expiries (weekly: Feb 2019 - Nov 2026)",
                 x=0.04, ha="left", fontsize=13, color=INK, y=1.03)
    fig.text(0.04, -0.07, "Source: NSE daily index closing reports (Nifty 50, India VIX) and NSE F&O bhavcopy "
             "(2026 straddles). 'Before expiry' counts any intraday touch between the forecast day and expiry.",
             fontsize=7, color=MUTED, ha="left")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
