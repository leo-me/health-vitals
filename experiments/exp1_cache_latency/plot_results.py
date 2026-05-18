"""
Generate charts for Exp 1 — Cache Layer Response Time.

Outputs (saved to results/):
    latency_comparison.png  — grouped bar chart: p50/p95/p99 × 3 concurrency levels
    rps_comparison.png      — bar chart: RPS cache OFF vs ON
    timeseries.png          — p95 over time for all 6 runs
    combined.png            — all three panels in one figure (thesis-ready)

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

# ── raw data (from *_stats.csv) ───────────────────────────────────────────────
STATS = {
    ("u=1",  "Cache OFF"): dict(p50=170,  p95=260,  p99=300,  avg=168,  rps=3.36),
    ("u=1",  "Cache ON" ): dict(p50=170,  p95=280,  p99=420,  avg=171,  rps=3.33),
    ("u=10", "Cache OFF"): dict(p50=280,  p95=560,  p99=730,  avg=298,  rps=22.67),
    ("u=10", "Cache ON" ): dict(p50=310,  p95=660,  p99=840,  avg=333,  rps=20.93),
    ("u=50", "Cache OFF"): dict(p50=1700, p95=2500, p99=2800, avg=1675, rps=25.17),
    ("u=50", "Cache ON" ): dict(p50=1900, p95=3100, p99=4000, avg=1898, rps=22.37),
}

LEVELS  = ["u=1", "u=10", "u=50"]
MODES   = ["Cache OFF", "Cache ON"]
COLOR   = {"Cache OFF": "#4C72B0", "Cache ON": "#DD8452"}   # blue / orange

# ── style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":  "DejaVu Sans",
    "font.size":    11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "axes.grid.axis":    "y",
    "grid.alpha":        0.35,
    "figure.dpi":        150,
})


# ── helpers ───────────────────────────────────────────────────────────────────

def _bar_group(ax, levels, off_vals, on_vals, ylabel, title, ylim=None):
    x     = np.arange(len(levels))
    width = 0.38
    b1 = ax.bar(x - width / 2, off_vals, width, label="Cache OFF",
                color=COLOR["Cache OFF"], edgecolor="white", linewidth=0.6)
    b2 = ax.bar(x + width / 2, on_vals,  width, label="Cache ON",
                color=COLOR["Cache ON"],  edgecolor="white", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(levels)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight="bold", pad=8)
    if ylim:
        ax.set_ylim(0, ylim)
    ax.legend(framealpha=0.7)
    # value labels on bars
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + max(h * 0.02, 5),
                f"{int(h):,}", ha="center", va="bottom", fontsize=9)


# ── Figure 1: latency comparison ──────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=False)
fig.suptitle("Exp 1 — Response Latency: Cache OFF vs Cache ON", fontsize=13, fontweight="bold", y=1.01)

for ax, pct in zip(axes, ["p50", "p95", "p99"]):
    off = [STATS[(lv, "Cache OFF")][pct] for lv in LEVELS]
    on  = [STATS[(lv, "Cache ON" )][pct] for lv in LEVELS]
    _bar_group(ax, LEVELS, off, on, "Response Time (ms)", f"{pct} Latency")

plt.tight_layout()
out = RESULTS / "latency_comparison.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 2: RPS comparison ──────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(6, 4))
off_rps = [STATS[(lv, "Cache OFF")]["rps"] for lv in LEVELS]
on_rps  = [STATS[(lv, "Cache ON" )]["rps"] for lv in LEVELS]
_bar_group(ax, LEVELS, off_rps, on_rps, "Requests / second", "Throughput: Cache OFF vs Cache ON")
fig.suptitle("Exp 1 — RPS Comparison", fontsize=13, fontweight="bold")
plt.tight_layout()
out = RESULTS / "rps_comparison.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 3: p95 time-series ─────────────────────────────────────────────────

RUNS = [
    ("u1_no_cache",  "u=1  Cache OFF",  "#4C72B0", "--"),
    ("u1_cache",     "u=1  Cache ON",   "#4C72B0", "-"),
    ("u10_no_cache", "u=10 Cache OFF",  "#DD8452", "--"),
    ("u10_cache",    "u=10 Cache ON",   "#DD8452", "-"),
    ("u50_no_cache", "u=50 Cache OFF",  "#55A868", "--"),
    ("u50_cache",    "u=50 Cache ON",   "#55A868", "-"),
]

fig, ax = plt.subplots(figsize=(12, 5))

for run_id, label, color, ls in RUNS:
    path = RESULTS / f"{run_id}_stats_history.csv"
    if not path.exists():
        continue
    df = pd.read_csv(path)
    df = df[df["Name"] == "Aggregated"].copy()
    df = df[df["95%"] != "N/A"]
    df["95%"] = pd.to_numeric(df["95%"], errors="coerce")
    df = df.dropna(subset=["95%"])
    if df.empty:
        continue
    t0 = df["Timestamp"].iloc[0]
    ax.plot(df["Timestamp"] - t0, df["95%"],
            color=color, linestyle=ls, linewidth=1.8, label=label, alpha=0.85)

ax.set_xlabel("Elapsed time (s)")
ax.set_ylabel("p95 Response Time (ms)")
ax.set_title("Exp 1 — p95 Latency Over Time (all runs)", fontweight="bold")
ax.legend(fontsize=9, ncol=2, framealpha=0.7)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
plt.tight_layout()
out = RESULTS / "timeseries.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 4: combined (thesis figure) ───────────────────────────────────────

fig = plt.figure(figsize=(16, 10))
fig.suptitle(
    "Exp 1 — Redis Cache Layer: Impact on Response Latency and Throughput\n"
    "Endpoint: GET /api/v1/data/smart_watch/{user_id}  |  31 users  |  60 s per run",
    fontsize=12, fontweight="bold", y=1.01
)

gs = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.38)

# Row 0: p50, p95, p99
for col, pct in enumerate(["p50", "p95", "p99"]):
    ax = fig.add_subplot(gs[0, col])
    off = [STATS[(lv, "Cache OFF")][pct] for lv in LEVELS]
    on  = [STATS[(lv, "Cache ON" )][pct] for lv in LEVELS]
    _bar_group(ax, LEVELS, off, on, "ms", f"{pct} Latency")

# Row 1 left: RPS
ax_rps = fig.add_subplot(gs[1, 0])
_bar_group(ax_rps, LEVELS,
           [STATS[(lv, "Cache OFF")]["rps"] for lv in LEVELS],
           [STATS[(lv, "Cache ON" )]["rps"] for lv in LEVELS],
           "req/s", "Throughput (RPS)")

# Row 1 right (span 2 cols): time-series p95
ax_ts = fig.add_subplot(gs[1, 1:])
for run_id, label, color, ls in RUNS:
    path = RESULTS / f"{run_id}_stats_history.csv"
    if not path.exists():
        continue
    df = pd.read_csv(path)
    df = df[df["Name"] == "Aggregated"].copy()
    df = df[df["95%"] != "N/A"]
    df["95%"] = pd.to_numeric(df["95%"], errors="coerce")
    df = df.dropna(subset=["95%"])
    if df.empty:
        continue
    t0 = df["Timestamp"].iloc[0]
    ax_ts.plot(df["Timestamp"] - t0, df["95%"],
               color=color, linestyle=ls, linewidth=1.8, label=label, alpha=0.85)

ax_ts.set_xlabel("Elapsed time (s)")
ax_ts.set_ylabel("p95 (ms)")
ax_ts.set_title("p95 Latency Over Time", fontweight="bold")
ax_ts.legend(fontsize=8, ncol=2, framealpha=0.7)
ax_ts.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))

out = RESULTS / "combined.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)

print("\nAll charts saved to", RESULTS)
