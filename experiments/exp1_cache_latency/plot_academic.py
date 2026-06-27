"""
Generate academic-style charts for Exp 1 — Cache Layer Response Time.

Figures produced in results/:
    mean_sd.png          — mean ± SD, 3 phases, Cache OFF vs ON, error bars
    percentiles.png      — p50 / p90 / p95 grid, 3 phases × 3 percentiles
    academic_combined.png — thesis-ready combined figure

Usage (from exp1_cache_latency/):
    python plot_academic.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

HERE    = Path(__file__).resolve().parent
RESULTS = HERE / "results"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "axes.grid.axis":    "y",
    "grid.alpha":        0.25,
    "figure.dpi":        150,
})

PHASES = [
    ("smart_watch", "Phase 1 — smart_watch\n(6× LIMIT 1, TTL=5 s)", ""),
    ("overview",    "Phase 2 — overview\n(GROUP BY aggregate, TTL=60 s)", "overview_"),
    ("cheap",       "Phase 3 — cheap\n(1× LIMIT 1, TTL=5 s)",  "cheap_"),
]
LEVELS       = [1, 10, 50]
LEVEL_LABELS = ["u = 1", "u = 10", "u = 50"]
MODES        = ["no_cache", "cache"]
COLOR        = {"no_cache": "#4C72B0", "cache": "#DD8452"}
LABEL        = {"no_cache": "Cache OFF", "cache": "Cache ON"}


# ── data loading ──────────────────────────────────────────────────────────────

def _load_stats(prefix: str, u: int, mode: str) -> dict | None:
    path = RESULTS / f"{prefix}u{u}_{mode}_stats.csv"
    if not path.exists():
        return None
    df  = pd.read_csv(path)
    agg = df[df["Name"] == "Aggregated"].iloc[0]
    return {
        "p50": float(agg["50%"]),
        "p90": float(agg["90%"]),
        "p95": float(agg["95%"]),
        "p99": float(agg["99%"]),
        "avg": float(agg["Average Response Time"]),
        "rps": float(agg["Requests/s"]),
        "n":   int(agg["Request Count"]),
    }


def _compute_mean_sd(prefix: str, u: int, mode: str) -> tuple[float, float]:
    """Return (mean, sd) computed from per-interval averages in stats_history."""
    path = RESULTS / f"{prefix}u{u}_{mode}_stats_history.csv"
    if not path.exists():
        return float("nan"), float("nan")
    df = pd.read_csv(path)
    df = df[df["Name"] == "Aggregated"].copy()
    df = df[df["Total Request Count"] > 0].reset_index(drop=True)
    if df.empty:
        return float("nan"), float("nan")

    n     = df["Total Request Count"].values
    avg   = df["Total Average Response Time"].values
    total = n * avg

    intervals = [avg[0]]
    for i in range(1, len(df)):
        dn = n[i] - n[i - 1]
        if dn > 0:
            intervals.append((total[i] - total[i - 1]) / dn)

    arr = np.array(intervals)
    return arr.mean(), arr.std(ddof=1)


# Build data tables
DATA: dict = {}
for phase_key, _, prefix in PHASES:
    DATA[phase_key] = {}
    for u in LEVELS:
        DATA[phase_key][u] = {}
        for mode in MODES:
            s = _load_stats(prefix, u, mode) or {}
            mean, sd = _compute_mean_sd(prefix, u, mode)
            DATA[phase_key][u][mode] = {**s, "mean": mean, "sd": sd}


def _get(phase, u, mode, field):
    return DATA.get(phase, {}).get(u, {}).get(mode, {}).get(field, float("nan"))


# ── Figure 1: Mean ± SD ───────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), sharey=False)
fig.suptitle(
    "Exp 1 — Mean Response Time ± SD: Cache OFF vs Cache ON",
    fontsize=13, fontweight="bold", y=1.01,
)

x     = np.arange(len(LEVELS))
width = 0.38

for ax, (phase_key, phase_title, _) in zip(axes, PHASES):
    for offset, mode in [(-width / 2, "no_cache"), (width / 2, "cache")]:
        means = [_get(phase_key, u, mode, "mean") for u in LEVELS]
        sds   = [_get(phase_key, u, mode, "sd")   for u in LEVELS]
        bars  = ax.bar(
            x + offset, means, width,
            label=LABEL[mode], color=COLOR[mode],
            edgecolor="white", linewidth=0.6,
        )
        ax.errorbar(
            x + offset, means, yerr=sds,
            fmt="none", color="black", capsize=4, linewidth=1.4, capthick=1.4,
        )
        for bar, m in zip(bars, means):
            if np.isnan(m) or m <= 0:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2, m * 1.05,
                f"{m:.0f}", ha="center", va="bottom", fontsize=7.5,
            )

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(LEVEL_LABELS)
    ax.set_ylabel("Response Time (ms, log scale)")
    ax.set_title(phase_title, fontweight="bold", pad=8)
    ax.legend(framealpha=0.75, fontsize=9)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))

plt.tight_layout()
out = RESULTS / "mean_sd.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 2: Percentile grid (p50 / p90 / p95) ──────────────────────────────

PCTS = [("p50", "p50"), ("p90", "p90"), ("p95", "p95")]

fig, axes = plt.subplots(3, 3, figsize=(15, 13), sharex=True)
fig.suptitle(
    "Exp 1 — Response Latency Percentiles (p50 / p90 / p95): Cache OFF vs Cache ON",
    fontsize=13, fontweight="bold", y=1.002,
)

for row, (phase_key, phase_title, _) in enumerate(PHASES):
    for col, (pct_key, pct_label) in enumerate(PCTS):
        ax = axes[row, col]
        for offset, mode in [(-width / 2, "no_cache"), (width / 2, "cache")]:
            vals = [_get(phase_key, u, mode, pct_key) for u in LEVELS]
            bars = ax.bar(
                x + offset, vals, width,
                label=LABEL[mode], color=COLOR[mode],
                edgecolor="white", linewidth=0.6,
            )
            for bar, v in zip(bars, vals):
                if np.isnan(v) or v <= 0:
                    continue
                ax.text(
                    bar.get_x() + bar.get_width() / 2, v * 1.08,
                    f"{v:.0f}", ha="center", va="bottom", fontsize=7.5,
                )

        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xticklabels(LEVEL_LABELS)
        ax.set_title(f"{pct_label}", fontweight="bold", pad=6)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        if col == 0:
            ax.set_ylabel(f"{phase_title}\n\nResponse Time (ms, log)")
        if col > 0:
            ax.set_ylabel("Response Time (ms, log)")
        if row == 0:
            ax.legend(framealpha=0.75, fontsize=8)

plt.tight_layout()
out = RESULTS / "percentiles.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 3: Academic combined ───────────────────────────────────────────────
# Top row: mean ± SD (3 panels)
# Bottom row: p50 / p95 side-by-side speedup summary

fig = plt.figure(figsize=(18, 11))
fig.suptitle(
    "Exp 1 — Redis Cache Layer · 3 Phases · 3 Concurrency Levels · 60 s runs · 25 users\n"
    "Primary metric: mean ± SD (temporal stability) · Supplementary: p50 / p95",
    fontsize=12, fontweight="bold", y=1.005,
)
gs = fig.add_gridspec(2, 3, hspace=0.52, wspace=0.35)

# ── top row: mean ± SD ────────────────────────────────────────────────────────
for col, (phase_key, phase_title, _) in enumerate(PHASES):
    ax = fig.add_subplot(gs[0, col])
    for offset, mode in [(-width / 2, "no_cache"), (width / 2, "cache")]:
        means = [_get(phase_key, u, mode, "mean") for u in LEVELS]
        sds   = [_get(phase_key, u, mode, "sd")   for u in LEVELS]
        bars  = ax.bar(
            x + offset, means, width,
            label=LABEL[mode], color=COLOR[mode],
            edgecolor="white", linewidth=0.6,
        )
        ax.errorbar(
            x + offset, means, yerr=sds,
            fmt="none", color="black", capsize=4, linewidth=1.4, capthick=1.4,
        )
        for bar, m in zip(bars, means):
            if np.isnan(m) or m <= 0:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2, m * 1.05,
                f"{m:.0f}", ha="center", va="bottom", fontsize=7.5,
            )
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(LEVEL_LABELS)
    ax.set_ylabel("Response Time (ms, log)")
    ax.set_title(f"Mean ± SD\n{phase_title}", fontweight="bold", pad=6, fontsize=10)
    ax.legend(framealpha=0.75, fontsize=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))

# ── bottom row: p50, p95, speedup (mean-based) ───────────────────────────────
for col, (pct_key, pct_label) in enumerate([("p50", "p50"), ("p95", "p95")]):
    ax = fig.add_subplot(gs[1, col])
    for pi, (phase_key, phase_title, _) in enumerate(PHASES):
        bar_w = 0.12
        phase_step = 0.29
        shift = (pi - 1) * phase_step
        phase_colors = ["#55A868", "#C44E52", "#8172B2"]
        for offset, mode in [(-bar_w / 2, "no_cache"), (bar_w / 2, "cache")]:
            vals = [_get(phase_key, u, mode, pct_key) for u in LEVELS]
            hatch = "//" if mode == "no_cache" else ""
            label = f"P{pi+1} {'OFF' if mode=='no_cache' else 'ON'}" if col == 0 else None
            ax.bar(
                x + shift + offset, vals, bar_w,
                label=label, color=phase_colors[pi],
                hatch=hatch, edgecolor="white", linewidth=0.5, alpha=0.85,
            )
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(LEVEL_LABELS)
    ax.set_ylabel(f"{pct_label} Response Time (ms, log)")
    ax.set_title(f"{pct_label} — all phases", fontweight="bold", pad=6)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    if col == 0:
        ax.legend(fontsize=7, ncol=3, framealpha=0.75, loc="upper left")

# bottom-right: mean speedup (Cache OFF mean / Cache ON mean)
ax_sp = fig.add_subplot(gs[1, 2])
phase_colors = ["#55A868", "#C44E52", "#8172B2"]
sp_bar_w     = 0.18
sp_step      = 0.24
for pi, (phase_key, phase_title, _) in enumerate(PHASES):
    shift = (pi - 1) * sp_step
    speedups = []
    for u in LEVELS:
        m_off = _get(phase_key, u, "no_cache", "mean")
        m_on  = _get(phase_key, u, "cache",    "mean")
        speedups.append(m_off / m_on if m_on > 0 else float("nan"))
    bars = ax_sp.bar(
        x + shift, speedups, sp_bar_w,
        label=f"Phase {pi+1}", color=phase_colors[pi],
        edgecolor="white", linewidth=0.5,
    )
    for bar, v in zip(bars, speedups):
        if np.isnan(v):
            continue
        ax_sp.text(
            bar.get_x() + bar.get_width() / 2, v * 1.12,
            f"{v:.0f}×", ha="center", va="bottom", fontsize=7.5, fontweight="bold",
        )

ax_sp.set_yscale("log")
ax_sp.set_xticks(x)
ax_sp.set_xticklabels(LEVEL_LABELS)
ax_sp.set_xlim(-0.7, 2.85)
ax_sp.axhline(1.0, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax_sp.text(-0.65, 1.15, "1× (no gain)", fontsize=8, color="gray")
ax_sp.set_ylabel("Mean speedup (OFF / ON, log)")
ax_sp.set_title("Mean speedup — all phases", fontweight="bold", pad=6)
ax_sp.legend(fontsize=8, framealpha=0.75)
ax_sp.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}×"))

out = RESULTS / "academic_combined.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)

print("\nAll academic charts saved to", RESULTS)
