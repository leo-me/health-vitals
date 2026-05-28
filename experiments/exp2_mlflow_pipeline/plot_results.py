"""
Generate charts for Exp 2 — MLflow Model Registry Pipeline (final design).

New design: standard scenario only, feature_version=v1 fixed, 3 dataset sizes × 3 thresholds = 9 cells.
No feature-version or scenario dimensions in the plots.

Outputs (saved to results/):
    accuracy_overview.png   — accuracy by dataset size, threshold lines
    duration_scaling.png    — training time across dataset sizes (log scale)
    gap_to_threshold.png    — accuracy gap to each threshold per size
    retrain_behavior.png    — retrain trigger rate per size
    combined.png            — all panels in one thesis-ready figure

Usage (from project root):
    python experiments/exp2_mlflow_pipeline/plot_results.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# ── paths ─────────────────────────────────────────────────────────────────────
HERE      = Path(__file__).resolve().parent
CSV_CLEAN = HERE / "results" / "pipeline_results_clean.csv"
CSV_RAW   = HERE / "results" / "pipeline_results.csv"
CSV       = CSV_CLEAN if CSV_CLEAN.exists() else CSV_RAW
RESULTS   = HERE / "results"

df = pd.read_csv(CSV)
print(f"loaded {len(df)} rows from {CSV.name}")

# ── constants ─────────────────────────────────────────────────────────────────
SIZE_LABEL_MAP = {1_000: "small\n(1 K)", 50_000: "medium\n(50 K)", 400_000: "large\n(400 K)"}
SIZES       = sorted(df["dataset_size"].unique().tolist())
SIZE_LABELS = [SIZE_LABEL_MAP[s] for s in SIZES]
THRESHOLDS  = [0.50, 0.55, 0.60]
THR_COLORS  = ["#2ca02c", "#ff7f0e", "#d62728"]
BAR_COLOR   = "#4C72B0"

# Use only initial runs (retrain_count=0) for accuracy/registration stats
initial = df[df["retrain_count"] == 0].copy()

# ── style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "axes.grid.axis":    "y",
    "grid.alpha":        0.35,
    "figure.dpi":        150,
})


# ── Figure 1: accuracy overview ───────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(8, 5))
fig.suptitle(
    "Exp 2 — Model Accuracy by Dataset Size\n"
    "(dashed lines = registration thresholds)",
    fontsize=12, fontweight="bold"
)

acc_by_size = initial.groupby("dataset_size")["accuracy"].mean()
vals = [acc_by_size.get(s, np.nan) for s in SIZES]
x    = np.arange(len(SIZES))
bars = ax.bar(x, vals, 0.5, color=BAR_COLOR, edgecolor="white", linewidth=0.6)
for bar, v in zip(bars, vals):
    if not np.isnan(v):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.003,
                f"{v:.4f}", ha="center", va="bottom", fontsize=9)

for thr, tc in zip(THRESHOLDS, THR_COLORS):
    ax.axhline(thr, color=tc, linestyle="--", linewidth=1.3, alpha=0.85, label=f"thr = {thr}")

ax.set_xticks(x)
ax.set_xticklabels(SIZE_LABELS)
ax.set_xlabel("Dataset Size")
ax.set_ylabel("Mean Accuracy (initial run)")
ax.set_ylim(0.48, 0.65)
ax.legend(fontsize=9, framealpha=0.7)

plt.tight_layout()
out = RESULTS / "accuracy_overview.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 2: training duration scaling ───────────────────────────────────────

fig, ax = plt.subplots(figsize=(8, 5))

# Use median training duration per size (excludes the 1677s outlier from memory pressure)
dur_by_size = initial.groupby("dataset_size")["duration_seconds"].median()
vals = [dur_by_size.get(s, np.nan) for s in SIZES]
bars = ax.bar(x, vals, 0.5, color=BAR_COLOR, edgecolor="white", linewidth=0.6)
for bar, v in zip(bars, vals):
    if not np.isnan(v):
        lbl = f"{v:.2f}s" if v < 60 else f"{v:.0f}s ({v/60:.1f}m)"
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.12,
                lbl, ha="center", va="bottom", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(SIZE_LABELS)
ax.set_xlabel("Dataset Size")
ax.set_ylabel("Training Duration (seconds, log scale)")
ax.set_yscale("log")
ax.set_title(
    "Training Duration Scaling\n"
    "RandomForestClassifier (n_estimators=100, feature_version=v1)",
    fontweight="bold"
)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda v, _: f"{v:.2f}s" if v < 1 else (f"{int(v)}s" if v < 60 else f"{v/60:.0f}m")
))

plt.tight_layout()
out = RESULTS / "duration_scaling.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 3: accuracy gap to threshold ───────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
fig.suptitle(
    "Exp 2 — Accuracy Gap to Registration Threshold\n"
    "(positive = registered; negative = retrain branch triggered)",
    fontsize=12, fontweight="bold"
)

acc_by_size_thr = initial.groupby(["dataset_size", "threshold"])["accuracy"].mean()

for ax, thr, tc in zip(axes, THRESHOLDS, THR_COLORS):
    gaps  = [acc_by_size_thr.get((s, thr), np.nan) - thr for s in SIZES]
    colors = [("#2ca02c" if g > 0 else "#d62728") for g in gaps]
    bars   = ax.bar(x, gaps, 0.5, color=colors, edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, gaps):
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    v + 0.003 if v >= 0 else v - 0.003,
                    f"{v:+.4f}", ha="center",
                    va="bottom" if v >= 0 else "top", fontsize=9)
    ax.axhline(0, color="black", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(SIZE_LABELS)
    ax.set_xlabel("Dataset Size")
    ax.set_ylabel("Accuracy − Threshold" if ax == axes[0] else "")
    ax.set_title(f"Threshold = {thr}", fontweight="bold", color=tc)

plt.tight_layout()
out = RESULTS / "gap_to_threshold.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 4: retrain behavior ────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(7, 4))

# retrain rate = fraction of initial pipeline calls that failed (across all 3 thresholds)
retrain_rate = initial.groupby("dataset_size")["registered"].apply(
    lambda s: (1 - s.mean()) * 100
)
vals = [retrain_rate.get(s, 0) for s in SIZES]
bars = ax.bar(x, vals, 0.5, color=BAR_COLOR, edgecolor="white", linewidth=0.6)
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5,
            f"{v:.0f}%", ha="center", va="bottom", fontsize=10)

ax.set_xticks(x)
ax.set_xticklabels(SIZE_LABELS)
ax.set_xlabel("Dataset Size")
ax.set_ylabel("% of pipeline calls triggering retrain")
ax.set_title(
    "Automatic Retrain Trigger Rate\n"
    "(across all 3 thresholds; thr=0.60 always fails)",
    fontweight="bold"
)
ax.set_ylim(0, 60)

plt.tight_layout()
out = RESULTS / "retrain_behavior.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 5: combined thesis figure ─────────────────────────────────────────

fig = plt.figure(figsize=(16, 10))
fig.suptitle(
    "Exp 2 — MLflow Model Registry Pipeline: Training, Evaluation, and Registration\n"
    "RandomForest (n_estimators=100, feature_version=v1)  |  "
    "3 dataset sizes × 3 thresholds = 9 pipeline calls  |  standard scenario",
    fontsize=11, fontweight="bold", y=1.01
)

gs = fig.add_gridspec(2, 3, hspace=0.52, wspace=0.38)

# ── Row 0: accuracy + duration ─────────────────────────────────────────────
ax_acc = fig.add_subplot(gs[0, 0:2])
vals_acc = [acc_by_size.get(s, np.nan) for s in SIZES]
bars = ax_acc.bar(x, vals_acc, 0.5, color=BAR_COLOR, edgecolor="white", linewidth=0.6)
for bar, v in zip(bars, vals_acc):
    if not np.isnan(v):
        ax_acc.text(bar.get_x() + bar.get_width() / 2, v + 0.003,
                    f"{v:.4f}", ha="center", va="bottom", fontsize=8.5)
for thr, tc in zip(THRESHOLDS, THR_COLORS):
    ax_acc.axhline(thr, color=tc, linestyle="--", linewidth=1.2, alpha=0.85, label=f"thr={thr}")
ax_acc.set_xticks(x); ax_acc.set_xticklabels(SIZE_LABELS, fontsize=9)
ax_acc.set_ylabel("Mean Accuracy"); ax_acc.set_ylim(0.48, 0.65)
ax_acc.set_title("Accuracy by Dataset Size", fontweight="bold")
ax_acc.legend(fontsize=8.5, framealpha=0.7)

ax_dur = fig.add_subplot(gs[0, 2])
vals_dur = [dur_by_size.get(s, np.nan) for s in SIZES]
bars = ax_dur.bar(x, vals_dur, 0.5, color=BAR_COLOR, edgecolor="white", linewidth=0.6)
for bar, v in zip(bars, vals_dur):
    if not np.isnan(v):
        lbl = f"{v:.2f}s" if v < 1 else (f"{int(v)}s" if v < 60 else f"{v:.0f}s")
        ax_dur.text(bar.get_x() + bar.get_width() / 2, v * 1.15,
                    lbl, ha="center", va="bottom", fontsize=8.5)
ax_dur.set_xticks(x); ax_dur.set_xticklabels(SIZE_LABELS, fontsize=9)
ax_dur.set_yscale("log"); ax_dur.set_ylabel("Duration (s, log)")
ax_dur.set_title("Training Duration Scaling", fontweight="bold")
ax_dur.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda v, _: f"{v:.2f}s" if v < 1 else (f"{int(v)}s" if v < 60 else f"{v/60:.0f}m")
))

# ── Row 1: gap to threshold × 3 panels ────────────────────────────────────
for col, (thr, tc) in enumerate(zip(THRESHOLDS, THR_COLORS)):
    ax = fig.add_subplot(gs[1, col])
    gaps   = [acc_by_size_thr.get((s, thr), np.nan) - thr for s in SIZES]
    colors = [("#2ca02c" if g > 0 else "#d62728") for g in gaps]
    bars   = ax.bar(x, gaps, 0.5, color=colors, edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, gaps):
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    v + 0.002 if v >= 0 else v - 0.002,
                    f"{v:+.4f}", ha="center",
                    va="bottom" if v >= 0 else "top", fontsize=8.5)
    ax.axhline(0, color="black", linewidth=1.0)
    ax.set_xticks(x); ax.set_xticklabels(SIZE_LABELS, fontsize=9)
    ax.set_ylabel("Accuracy − Threshold" if col == 0 else "")
    ax.set_title(f"Gap to Threshold = {thr}", fontweight="bold", color=tc)

out = RESULTS / "combined.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)

print(f"\nAll charts saved to {RESULTS}")
