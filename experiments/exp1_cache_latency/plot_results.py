"""
Generate charts for Exp 1 — Cache Layer Response Time (v2: two-phase).

Reads stats CSVs from results/ and produces:

    latency_grid.png   — 2×3 grid: rows = phase 1 / phase 2, cols = p50/p95/p99
    speedup_bars.png   — bar chart of cache speedup factor per (phase, u)
    rps_grid.png       — RPS comparison side-by-side for both phases
    timeseries.png     — p95 over time, two panels (phase 1 / phase 2)
    combined.png       — everything in one thesis-ready figure

Usage (from project root):
    python experiments/exp1_cache_latency/plot_results.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ── paths ─────────────────────────────────────────────────────────────────────
HERE    = Path(__file__).resolve().parent
RESULTS = HERE / "results"

# ── style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":  "DejaVu Sans",
    "font.size":    11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "axes.grid.axis":    "y",
    "grid.alpha":        0.30,
    "figure.dpi":        150,
})

PHASES = [
    ("phase1", "Phase 1 — cheap (1× LIMIT 1)",          "cheap_"),
    ("phase2", "Phase 2 — overview (heavy aggregate)",  "overview_"),
]
LEVELS  = [1, 10, 50]
LEVEL_LABELS = [f"u={u}" for u in LEVELS]
MODES   = ["no_cache", "cache"]
MODE_LABELS = {"no_cache": "Cache OFF", "cache": "Cache ON"}
COLOR   = {"no_cache": "#4C72B0", "cache": "#DD8452"}


# ── loader ────────────────────────────────────────────────────────────────────

def _load_stats(prefix_base: str, u: int, mode: str) -> dict | None:
    path = RESULTS / f"{prefix_base}u{u}_{mode}_stats.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    agg = df[df["Name"] == "Aggregated"].iloc[0]
    return {
        "n":     int(agg["Request Count"]),
        "fails": int(agg["Failure Count"]),
        "p50":   float(agg["50%"]),
        "p95":   float(agg["95%"]),
        "p99":   float(agg["99%"]),
        "avg":   float(agg["Average Response Time"]),
        "rps":   float(agg["Requests/s"]),
    }


# Build a nested dict: STATS[phase_key][u][mode] = row
STATS: dict[str, dict[int, dict[str, dict]]] = {}
for phase_key, _, prefix_base in PHASES:
    STATS[phase_key] = {}
    for u in LEVELS:
        STATS[phase_key][u] = {}
        for mode in MODES:
            row = _load_stats(prefix_base, u, mode)
            if row is None:
                print(f"  ⚠️  missing: phase={phase_key} u={u} mode={mode}")
            else:
                STATS[phase_key][u][mode] = row


# ── helpers ───────────────────────────────────────────────────────────────────

def _bar_group(ax, levels, off_vals, on_vals, ylabel, title, ylog=False, fmt="{:,.0f}"):
    x     = np.arange(len(levels))
    width = 0.38
    b1 = ax.bar(x - width / 2, off_vals, width, label="Cache OFF",
                color=COLOR["no_cache"], edgecolor="white", linewidth=0.6)
    b2 = ax.bar(x + width / 2, on_vals,  width, label="Cache ON",
                color=COLOR["cache"],    edgecolor="white", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(levels)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight="bold", pad=8)
    if ylog:
        ax.set_yscale("log")
    ax.legend(framealpha=0.7, fontsize=9)
    # value labels on bars
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        if h <= 0: continue
        offset = h * 0.04 if not ylog else h * 0.15
        ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                fmt.format(h), ha="center", va="bottom", fontsize=8)


def _safe_get(phase, u, mode, field):
    """Return field or NaN if missing."""
    return STATS.get(phase, {}).get(u, {}).get(mode, {}).get(field, float("nan"))


# ── Figure 1: latency_grid (2 phases × 3 percentiles) ────────────────────────

fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True)
fig.suptitle(
    "Exp 1 — Response Latency: Cache OFF vs Cache ON (log scale)",
    fontsize=13, fontweight="bold", y=0.995,
)

for row, (phase_key, phase_title, _) in enumerate(PHASES):
    for col, pct in enumerate(["p50", "p95", "p99"]):
        ax = axes[row, col]
        off = [_safe_get(phase_key, u, "no_cache", pct) for u in LEVELS]
        on  = [_safe_get(phase_key, u, "cache",    pct) for u in LEVELS]
        title_prefix = "Phase 1" if phase_key == "phase1" else "Phase 2"
        _bar_group(ax, LEVEL_LABELS, off, on, "ms", f"{title_prefix}  ·  {pct}", ylog=True)
    # left-most label for the row
    axes[row, 0].set_ylabel(f"{phase_title}\n\nResponse Time (ms)")

plt.tight_layout()
out = RESULTS / "latency_grid.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 2: speedup bars ────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 5.5))
x = np.arange(len(LEVELS))
width = 0.38
speedups_p1 = []
speedups_p2 = []
for u in LEVELS:
    off1 = _safe_get("phase1", u, "no_cache", "p50")
    on1  = _safe_get("phase1", u, "cache",    "p50")
    off2 = _safe_get("phase2", u, "no_cache", "p50")
    on2  = _safe_get("phase2", u, "cache",    "p50")
    speedups_p1.append(off1 / on1 if on1 > 0 else float("nan"))
    speedups_p2.append(off2 / on2 if on2 > 0 else float("nan"))

b1 = ax.bar(x - width/2, speedups_p1, width,
            label="Phase 1 (cheap)",    color="#55A868", edgecolor="white")
b2 = ax.bar(x + width/2, speedups_p2, width,
            label="Phase 2 (overview)", color="#C44E52", edgecolor="white")
for bar, val in [(b1, speedups_p1), (b2, speedups_p2)]:
    for rect, v in zip(bar, val):
        h = rect.get_height()
        if np.isnan(h): continue
        ax.text(rect.get_x() + rect.get_width()/2, h*1.1, f"{v:.0f}×",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(LEVEL_LABELS)
ax.set_yscale("log")
ax.set_ylabel("p50 speedup (OFF / ON)  —  log scale")
ax.axhline(1.0, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.text(2.4, 1.05, "1× (no gain)", fontsize=9, color="gray")
ax.set_title("Cache speedup: p50 (no_cache / cache)", fontweight="bold", pad=12)
ax.legend(framealpha=0.8)
plt.tight_layout()
out = RESULTS / "speedup_bars.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 3: RPS grid ────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)
for ax, (phase_key, phase_title, _) in zip(axes, PHASES):
    off = [_safe_get(phase_key, u, "no_cache", "rps") for u in LEVELS]
    on  = [_safe_get(phase_key, u, "cache",    "rps") for u in LEVELS]
    _bar_group(ax, LEVEL_LABELS, off, on, "Requests / second", phase_title, fmt="{:.1f}")

fig.suptitle("Exp 1 — Throughput (RPS): Cache OFF vs Cache ON",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = RESULTS / "rps_grid.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 4: time-series of p95 (2 panels) ──────────────────────────────────

def _plot_timeseries(ax, phase_key, prefix_base, title):
    runs = []
    for u in LEVELS:
        for mode in MODES:
            color = {1: "#4C72B0", 10: "#DD8452", 50: "#55A868"}[u]
            ls    = "--" if mode == "no_cache" else "-"
            runs.append((f"{prefix_base}u{u}_{mode}",
                         f"u={u} {MODE_LABELS[mode]}",
                         color, ls))
    for run_id, label, color, ls in runs:
        path = RESULTS / f"{run_id}_stats_history.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df = df[df["Name"] == "Aggregated"].copy()
        df = df[df["95%"] != "N/A"]
        df["95%"] = pd.to_numeric(df["95%"], errors="coerce")
        df = df.dropna(subset=["95%"])
        if df.empty: continue
        t0 = df["Timestamp"].iloc[0]
        ax.plot(df["Timestamp"] - t0, df["95%"],
                color=color, linestyle=ls, linewidth=1.8, label=label, alpha=0.85)
    ax.set_xlabel("Elapsed time (s)")
    ax.set_ylabel("p95 Response Time (ms)")
    ax.set_title(title, fontweight="bold")
    ax.set_yscale("log")
    ax.legend(fontsize=8, ncol=2, framealpha=0.7)

fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
for ax, (phase_key, phase_title, prefix_base) in zip(axes, PHASES):
    _plot_timeseries(ax, phase_key, prefix_base, phase_title)
fig.suptitle("Exp 1 — p95 Latency Over Time (log scale)",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = RESULTS / "timeseries.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 5: combined (thesis-ready) ────────────────────────────────────────

fig = plt.figure(figsize=(18, 12))
fig.suptitle(
    "Exp 1 — Redis Cache Layer · Phase 1 (cheap) vs Phase 2 (overview)\n"
    "12 runs · 3 concurrency × 2 cache states × 2 phases · 60 s each · 25 users · "
    "infra-db (6.75M sensor_recording rows)",
    fontsize=12, fontweight="bold", y=0.995,
)
gs = fig.add_gridspec(3, 3, hspace=0.55, wspace=0.32)

# Row 0–1: latency grid (2 phases × 3 percentiles)
for row, (phase_key, phase_title, _) in enumerate(PHASES):
    for col, pct in enumerate(["p50", "p95", "p99"]):
        ax = fig.add_subplot(gs[row, col])
        off = [_safe_get(phase_key, u, "no_cache", pct) for u in LEVELS]
        on  = [_safe_get(phase_key, u, "cache",    pct) for u in LEVELS]
        title_prefix = "Phase 1" if phase_key == "phase1" else "Phase 2"
        _bar_group(ax, LEVEL_LABELS, off, on, "ms", f"{title_prefix} · {pct}", ylog=True)
    fig.text(0.085, 0.78 - row*0.30, phase_title, rotation=90, fontsize=11,
             va="center", ha="center", fontweight="bold")

# Row 2: speedup (left), RPS combined (center), timeseries summary (right)
ax_sp = fig.add_subplot(gs[2, 0])
x = np.arange(len(LEVELS)); width = 0.38
ax_sp.bar(x - width/2, speedups_p1, width, label="Phase 1", color="#55A868", edgecolor="white")
ax_sp.bar(x + width/2, speedups_p2, width, label="Phase 2", color="#C44E52", edgecolor="white")
for i, (v1, v2) in enumerate(zip(speedups_p1, speedups_p2)):
    if not np.isnan(v1): ax_sp.text(i - width/2, v1*1.1, f"{v1:.0f}×", ha="center", fontsize=8, fontweight="bold")
    if not np.isnan(v2): ax_sp.text(i + width/2, v2*1.1, f"{v2:.0f}×", ha="center", fontsize=8, fontweight="bold")
ax_sp.set_xticks(x); ax_sp.set_xticklabels(LEVEL_LABELS)
ax_sp.set_yscale("log"); ax_sp.set_ylabel("p50 speedup (log)")
ax_sp.axhline(1.0, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax_sp.set_title("Cache speedup (p50)", fontweight="bold")
ax_sp.legend(framealpha=0.8, fontsize=8)

# Row 2 middle: RPS — phase 1 & 2 grouped 4 bars per u
ax_rps = fig.add_subplot(gs[2, 1])
width2 = 0.20
positions = []
for i, u in enumerate(LEVELS):
    positions.append(i)
for i, u in enumerate(LEVELS):
    p1_off = _safe_get("phase1", u, "no_cache", "rps")
    p1_on  = _safe_get("phase1", u, "cache",    "rps")
    p2_off = _safe_get("phase2", u, "no_cache", "rps")
    p2_on  = _safe_get("phase2", u, "cache",    "rps")
    ax_rps.bar(i - 1.5*width2, p1_off, width2, color="#4C72B0",
               label=("P1 OFF" if i==0 else None), edgecolor="white")
    ax_rps.bar(i - 0.5*width2, p1_on,  width2, color="#DD8452",
               label=("P1 ON"  if i==0 else None), edgecolor="white")
    ax_rps.bar(i + 0.5*width2, p2_off, width2, color="#4C72B0",
               hatch="//", label=("P2 OFF" if i==0 else None), edgecolor="white")
    ax_rps.bar(i + 1.5*width2, p2_on,  width2, color="#DD8452",
               hatch="//", label=("P2 ON"  if i==0 else None), edgecolor="white")
ax_rps.set_xticks(range(len(LEVELS))); ax_rps.set_xticklabels(LEVEL_LABELS)
ax_rps.set_ylabel("req/s"); ax_rps.set_title("Throughput (RPS)", fontweight="bold")
ax_rps.legend(fontsize=7, ncol=2, framealpha=0.7)

# Row 2 right: p95 over time, phase 2 (the dramatic one)
ax_ts = fig.add_subplot(gs[2, 2])
_plot_timeseries(ax_ts, "phase2", "overview_", "Phase 2 · p95 over time")

out = RESULTS / "combined.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)

print("\nAll charts saved to", RESULTS)
