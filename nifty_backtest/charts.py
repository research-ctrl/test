"""Charts for backtest.py (static PNG, light theme).

Encoding: predicted range = blue wash with blue High/Low ticks; actual High-Low = ink line;
a session whose actual range broke out of the band = status red with a triangle at the breakout
end (shape + label, so failure is never signalled by colour alone). Palette validated with the
dataviz validator (blue #2a78d6 / orange #eb6834: all checks pass on light surface #fcfcfb).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

SURFACE, PAGE = "#fcfcfb", "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, CRITICAL = "#2a78d6", "#eb6834", "#d03b3b"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10,
                     "axes.titleweight": "regular", "figure.facecolor": PAGE})


def _style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
        ax.spines[s].set_linewidth(0.8)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8, length=0, pad=4)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))


def _xticks(ax, dates):
    ax.set_xticks(np.arange(len(dates)))
    ax.set_xticklabels([pd.Timestamp(d).strftime("%d %b") for d in dates])
    ax.set_xlim(-0.7, len(dates) - 0.3)


def _band_panel(ax, d: pd.DataFrame, label_breakouts: bool, pending_label: bool = False) -> None:
    for i, r in enumerate(d.itertuples(index=False)):
        pending = not bool(r.scored)
        ax.add_patch(Rectangle((i - 0.3, r.pred_low), 0.6, r.pred_high - r.pred_low,
                               facecolor=BLUE, alpha=0.06 if pending else 0.13, edgecolor="none"))
        ax.hlines([r.pred_high, r.pred_low], i - 0.3, i + 0.3, colors=BLUE, linewidth=2,
                  linestyles="dotted" if pending else "solid")
        ax.hlines(r.prev_close, i - 0.12, i + 0.12, colors=MUTED, linewidth=1.5)
        if pending:
            if pending_label:
                ax.annotate("pending", (i, r.pred_low), xytext=(0, -5), textcoords="offset points",
                            ha="center", va="top", fontsize=7, color=INK2)
            continue
        fail = not bool(r.both_inside)
        col = CRITICAL if fail else INK
        ax.vlines(i, r.actual_low, r.actual_high, colors=col, linewidth=2.2, zorder=3)
        ax.plot([i, i], [r.actual_low, r.actual_high], ls="none", marker="o", ms=4.5, color=col,
                mec=SURFACE, mew=1.2, zorder=4)
        if fail:
            up = r.breakout_up >= r.breakout_down
            y, pts = (r.actual_high, r.breakout_up) if up else (r.actual_low, r.breakout_down)
            ax.plot(i, y, ls="none", marker="^" if up else "v", ms=7.5, color=CRITICAL, mec=SURFACE,
                    mew=1.2, zorder=5)
            if label_breakouts:
                ax.annotate(f"{'+' if up else '-'}{pts:.0f}", (i, y), xytext=(0, 7 if up else -7),
                            textcoords="offset points", ha="center", va="bottom" if up else "top",
                            fontsize=7.5, color=INK2)


def _legend_handles(d: pd.DataFrame, breakout_labels: bool = True):
    h = [Patch(facecolor=BLUE, alpha=0.25, edgecolor=BLUE, label="Predicted range (forecast at previous close)"),
         Line2D([], [], color=INK, lw=2.2, marker="o", ms=4.5, mec=SURFACE, label="Actual High-Low, inside band"),
         Line2D([], [], color=CRITICAL, lw=2.2, marker="^", ms=7, mec=SURFACE,
                label="Actual High-Low, broke out" + (" (label = points beyond band)" if breakout_labels else "")),
         Line2D([], [], color=MUTED, lw=1.5, label="Previous close")]
    pend = d.loc[~d["scored"].astype(bool), "target_date"]
    if len(pend):
        h.append(Line2D([], [], color=BLUE, lw=2, ls=":", label=f"Forecast for {', '.join(f'{x:%d %b}' for x in pend)}: "
                        "not scored, official NSE data not yet available"))
    return h


def hybrid_chart(sc: pd.DataFrame, path: Path, metrics: dict) -> None:
    d = sc[sc["model"] == "E_Hybrid_V1"].reset_index(drop=True)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(12, 8.2), height_ratios=[2.6, 1], sharex=True,
                                  gridspec_kw={"hspace": 0.12})
    _style(ax)
    _style(ax2)
    _band_panel(ax, d, label_breakouts=True, pending_label=True)
    _xticks(ax2, d["target_date"])
    ax.set_ylabel("NIFTY 50 (index points)", color=INK2)
    ax.legend(handles=_legend_handles(d), loc="upper left", frameon=False, fontsize=8, labelcolor=INK)
    fig.subplots_adjust(top=0.9)
    fig.suptitle("ATR + VIX Hybrid V1: predicted vs actual NIFTY 50 High/Low", x=0.06, ha="left",
                 fontsize=13, color=INK, y=0.955)
    ax.set_title(f"Forecast targets {d['target_date'].iloc[0]:%d %b} - {d['target_date'].iloc[-1]:%d %b %Y}, "
                 f"regular NSE sessions. Both extremes inside on {metrics['successful_sessions']} of "
                 f"{metrics['sessions']} scored sessions ({metrics['both_inside_pct']:.0f}%); "
                 f"MAE High {metrics['mae_high']:.0f} pts, MAE Low {metrics['mae_low']:.0f} pts.",
                 loc="left", color=INK2, fontsize=9, pad=8)
    # panel 2: predicted width vs actual range (same unit, one axis)
    x = np.arange(len(d))
    ax2.bar(x - 0.19, d["pred_width"], width=0.36, color=BLUE, label="Predicted width (2 x M)")
    ax2.bar(x + 0.19, d["actual_range"].fillna(0), width=0.36, color=ORANGE, label="Actual High-Low range")
    ax2.set_ylabel("Points", color=INK2)
    ax2.legend(loc="upper left", frameon=False, fontsize=8, ncols=2, labelcolor=INK)
    ax2.set_ylim(0, max(d["pred_width"].max(), d["actual_range"].max()) * 1.25)
    fig.text(0.06, 0.012, "Source: NSE daily index closing reports (ind_close_all), Nifty 50 cash index and "
             "India VIX. Forecast for each session uses only data available at the previous session's close.",
             fontsize=7, color=MUTED, ha="left")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=PAGE)
    plt.close(fig)


def all_models_chart(sc: pd.DataFrame, path: Path, summ: dict, models: dict) -> None:
    order = ["E_Hybrid_V1", "B_ATR_only", "C_VIX_only", "A_Camarilla_R4S4", "D_PrevDay_HL"]
    fig, axes = plt.subplots(len(order), 1, figsize=(12, 15), sharex=True, sharey=True,
                             gridspec_kw={"hspace": 0.38})
    for ax, m in zip(axes, order):
        _style(ax)
        d = sc[sc["model"] == m].reset_index(drop=True)
        _band_panel(ax, d, label_breakouts=False)
        s = summ[m]
        ax.set_title(f"{models[m][0]}  ({models[m][1]})   both inside {s['both_inside_pct']:.0f}%  |  "
                     f"MAE High {s['mae_high']:.0f} / Low {s['mae_low']:.0f} pts  |  avg width "
                     f"{s['avg_pred_width']:.0f} vs actual range {s['avg_actual_range']:.0f} pts",
                     loc="left", color=INK, fontsize=9, pad=6)
    first = sc[sc["model"] == order[0]]
    _xticks(axes[-1], first["target_date"])
    axes[0].legend(handles=_legend_handles(first, breakout_labels=False), loc="upper left", frameon=False,
                   fontsize=7.5, labelcolor=INK)
    fig.subplots_adjust(top=0.935)
    fig.suptitle("Five range models on the same sessions (regular NSE sessions, targets 19 Oct - 17 Nov 2026)",
                 x=0.06, ha="left", fontsize=13, color=INK, y=0.962)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=PAGE)
    plt.close(fig)
