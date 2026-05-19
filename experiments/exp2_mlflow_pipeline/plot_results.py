"""
Generate charts for Exp 2 — MLflow Model Registry Pipeline.

Outputs (saved to results/):
    accuracy_overview.png   — accuracy by dataset size × feature version, threshold lines
    duration_scaling.png    — training time across dataset sizes (log scale)
    gap_to_threshold.png    — accuracy gap to each threshold (shows registration barrier)
    retrain_behavior.png    — retrain trigger rate per configuration
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
HERE    = Path(__file__).resolve().parent
CSV     = HERE / "results" / "pipeline_results.csv"
RESULTS = HERE / "results"

df = pd.read_csv(CSV)

# ── derived columns ───────────────────────────────────────────────────────────
df["size_label"]  = df["dataset_size"].map({1_000: "small\n(1 K)", 50_000: "medium\n(50 K)", 500_000: "large\n(500 K)"})
df["size_order"]  = df["dataset_size"].map({1_000: 0, 50_000: 1, 500_000: 2})
df["scenario"]    = df["force_fail"].map({False: "Standard", True: "Forced-fail"})

SIZES      = [1_000, 50_000, 500_000]
SIZE_LABELS = ["small\n(1 K)", "medium\n(50 K)", "large\n(500 K)"]
FVS        = ["v1", "v2"]
#THRESHOLDS = [0.75, 0.80, 0.85]
THRESHOLDS = [0.50, 0.55, 0.60]
COLORS     = {"v1": "#4C72B0", "v2": "#DD8452"}
THR_COLORS = ["#2ca02c", "#ff7f0e", "#d62728"]

# ── style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":         "DejaVu Sans",
    "font.size":           11,
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "axes.grid":           True,
    "axes.grid.axis":      "y",
    "grid.alpha":          0.35,
    "figure.dpi":          150,
})


# ── Figure 1: accuracy overview ───────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
fig.suptitle(
    "Exp 2 — Model Accuracy by Dataset Size and Feature Version\n"
    "(dashed lines = thresholds; no run crossed any threshold)",
    fontsize=12, fontweight="bold"
)

for ax, (scenario, grp) in zip(axes, df.groupby("scenario")):
    x      = np.arange(len(SIZES))
    width  = 0.35
    for i, fv in enumerate(FVS):
        sub  = grp[grp["feature_version"] == fv].groupby("dataset_size")["accuracy"].mean()
        vals = [sub.get(s, np.nan) for s in SIZES]
        bars = ax.bar(x + (i - 0.5) * width, vals, width,
                      label=f"Feature {fv}", color=COLORS[fv],
                      edgecolor="white", linewidth=0.6)
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2, v + 0.003,
                        f"{v:.3f}", ha="center", va="bottom", fontsize=8)

    for thr, tc in zip(THRESHOLDS, THR_COLORS):
        ax.axhline(thr, color=tc, linestyle="--", linewidth=1.2, alpha=0.8,
                   label=f"thr={thr}")

    ax.set_xticks(x)
    ax.set_xticklabels(SIZE_LABELS)
    ax.set_xlabel("Dataset Size")
    ax.set_ylabel("Accuracy" if ax == axes[0] else "")
    ax.set_ylim(0.48, 0.92)
    ax.set_title(f"Scenario: {scenario}", fontweight="bold")
    ax.legend(fontsize=8, framealpha=0.7, ncol=2)

plt.tight_layout()
out = RESULTS / "accuracy_overview.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 2: training duration scaling ───────────────────────────────────────

fig, ax = plt.subplots(figsize=(8, 5))

dur = df.groupby(["dataset_size", "feature_version"])["duration_seconds"].mean().reset_index()

x     = np.arange(len(SIZES))
width = 0.35
for i, fv in enumerate(FVS):
    sub  = dur[dur["feature_version"] == fv].set_index("dataset_size")["duration_seconds"]
    vals = [sub.get(s, np.nan) for s in SIZES]
    bars = ax.bar(x + (i - 0.5) * width, vals, width,
                  label=f"Feature {fv}", color=COLORS[fv],
                  edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, vals):
        if not np.isnan(v):
            lbl = f"{v:.1f}s" if v < 60 else f"{v/60:.1f}m"
            ax.text(bar.get_x() + bar.get_width() / 2, v * 1.04,
                    lbl, ha="center", va="bottom", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(SIZE_LABELS)
ax.set_xlabel("Dataset Size")
ax.set_ylabel("Training Duration (seconds, log scale)")
ax.set_yscale("log")
ax.set_title("Training Duration Scaling (RandomForest, n_estimators=100)", fontweight="bold")
ax.legend(framealpha=0.7)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda v, _: f"{int(v)}s" if v < 60 else f"{v/60:.0f}m"
))

plt.tight_layout()
out = RESULTS / "duration_scaling.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 3: accuracy gap to threshold ───────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
fig.suptitle(
    "Exp 2 — Accuracy Gap to Registration Threshold\n"
    "(negative = failed; all bars are below zero → 0 registrations)",
    fontsize=12, fontweight="bold"
)

for ax, thr in zip(axes, THRESHOLDS):
    sub  = df.groupby(["dataset_size", "feature_version"])["accuracy"].mean().reset_index()
    sub["gap"] = sub["accuracy"] - thr
    x     = np.arange(len(SIZES))
    width = 0.35
    for i, fv in enumerate(FVS):
        s    = sub[sub["feature_version"] == fv].set_index("dataset_size")["gap"]
        vals = [s.get(sz, np.nan) for sz in SIZES]
        bars = ax.bar(x + (i - 0.5) * width, vals, width,
                      color=COLORS[fv], label=f"Feature {fv}",
                      edgecolor="white", linewidth=0.6)
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        v - 0.003 if v < 0 else v + 0.003,
                        f"{v:+.3f}", ha="center",
                        va="top" if v < 0 else "bottom", fontsize=8)

    ax.axhline(0, color="black", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(SIZE_LABELS)
    ax.set_xlabel("Dataset Size")
    ax.set_ylabel("Accuracy − Threshold" if ax == axes[0] else "")
    ax.set_title(f"Threshold = {thr}", fontweight="bold")
    ax.set_ylim(-0.35, 0.05)
    ax.legend(fontsize=9, framealpha=0.7)

plt.tight_layout()
out = RESULTS / "gap_to_threshold.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 4: retrain behavior ────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(7, 4))

# retrain_count=0 means initial run (first attempt), =1 means it was a retrain
# pipeline calls always produce both: count 0 (initial fail) and count 1 (retrain)
# We want: "% of pipeline calls that triggered a retrain"
pipeline = df[df["retrain_count"] == 0].copy()
pipeline["retrained"] = ~pipeline["registered"]  # failed → retrained

by_config = pipeline.groupby(["dataset_size", "feature_version"])["retrained"].mean() * 100

x     = np.arange(len(SIZES))
width = 0.35
for i, fv in enumerate(FVS):
    vals = [by_config.get((sz, fv), 0) for sz in SIZES]
    bars = ax.bar(x + (i - 0.5) * width, vals, width,
                  color=COLORS[fv], label=f"Feature {fv}",
                  edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1,
                f"{v:.0f}%", ha="center", va="bottom", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(SIZE_LABELS)
ax.set_xlabel("Dataset Size")
ax.set_ylabel("% of pipeline runs that triggered retrain")
ax.set_title("Automatic Retrain Trigger Rate\n(retrain fires when accuracy < threshold)",
             fontweight="bold")
ax.set_ylim(0, 115)
ax.legend(framealpha=0.7)

plt.tight_layout()
out = RESULTS / "retrain_behavior.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)


# ── Figure 5: combined thesis figure ─────────────────────────────────────────

fig = plt.figure(figsize=(18, 11))
fig.suptitle(
    "Exp 2 — MLflow Model Registry Pipeline: Training, Evaluation, and Registration\n"
    "RandomForest (n=100)  |  3 dataset sizes  |  3 thresholds  |  2 feature versions  |  2 scenarios",
    fontsize=12, fontweight="bold", y=1.01
)

gs = fig.add_gridspec(2, 4, hspace=0.48, wspace=0.38)

# Row 0: accuracy overview (standard) spanning 2 cols + (forced_fail) spanning 2 cols
for col_start, (scenario, grp) in enumerate(df.groupby("scenario")):
    ax = fig.add_subplot(gs[0, col_start * 2: col_start * 2 + 2])
    x  = np.arange(len(SIZES))
    width = 0.35
    for i, fv in enumerate(FVS):
        sub  = grp[grp["feature_version"] == fv].groupby("dataset_size")["accuracy"].mean()
        vals = [sub.get(s, np.nan) for s in SIZES]
        bars = ax.bar(x + (i - 0.5) * width, vals, width,
                      label=f"Feature {fv}", color=COLORS[fv],
                      edgecolor="white", linewidth=0.6)
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2, v + 0.004,
                        f"{v:.3f}", ha="center", va="bottom", fontsize=7.5)
    for thr, tc in zip(THRESHOLDS, THR_COLORS):
        ax.axhline(thr, color=tc, linestyle="--", linewidth=1.1, alpha=0.85,
                   label=f"thr={thr}")
    ax.set_xticks(x)
    ax.set_xticklabels(SIZE_LABELS, fontsize=9)
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.48, 0.92)
    ax.set_title(f"Accuracy — {scenario} scenario", fontweight="bold")
    ax.legend(fontsize=7.5, framealpha=0.7, ncol=2)

# Row 1 left: duration scaling
ax_dur = fig.add_subplot(gs[1, 0:2])
dur_mean = df.groupby(["dataset_size", "feature_version"])["duration_seconds"].mean().reset_index()
x = np.arange(len(SIZES))
for i, fv in enumerate(FVS):
    sub  = dur_mean[dur_mean["feature_version"] == fv].set_index("dataset_size")["duration_seconds"]
    vals = [sub.get(s, np.nan) for s in SIZES]
    bars = ax_dur.bar(x + (i - 0.5) * 0.35, vals, 0.35,
                      label=f"Feature {fv}", color=COLORS[fv],
                      edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, vals):
        if not np.isnan(v):
            lbl = f"{v:.1f}s" if v < 60 else f"{v/60:.1f}m"
            ax_dur.text(bar.get_x() + bar.get_width() / 2, v * 1.08,
                        lbl, ha="center", va="bottom", fontsize=8)
ax_dur.set_xticks(x)
ax_dur.set_xticklabels(SIZE_LABELS, fontsize=9)
ax_dur.set_yscale("log")
ax_dur.set_ylabel("Duration (s, log scale)")
ax_dur.set_title("Training Duration Scaling", fontweight="bold")
ax_dur.legend(framealpha=0.7)
ax_dur.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda v, _: f"{int(v)}s" if v < 60 else f"{v/60:.0f}m"
))

# Row 1 right: gap to threshold (thr=0.75 only, most lenient)
ax_gap = fig.add_subplot(gs[1, 2])
# thr = 0.75
thr = 0.50
sub_gap = df.groupby(["dataset_size", "feature_version"])["accuracy"].mean().reset_index()
sub_gap["gap"] = sub_gap["accuracy"] - thr
x = np.arange(len(SIZES))
for i, fv in enumerate(FVS):
    s    = sub_gap[sub_gap["feature_version"] == fv].set_index("dataset_size")["gap"]
    vals = [s.get(sz, np.nan) for sz in SIZES]
    bars = ax_gap.bar(x + (i - 0.5) * 0.35, vals, 0.35,
                      color=COLORS[fv], label=f"Feature {fv}",
                      edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, vals):
        if not np.isnan(v):
            ax_gap.text(bar.get_x() + bar.get_width() / 2, v - 0.004,
                        f"{v:+.3f}", ha="center", va="top", fontsize=8)
ax_gap.axhline(0, color="black", linewidth=1.0)
ax_gap.set_xticks(x)
ax_gap.set_xticklabels(SIZE_LABELS, fontsize=9)
ax_gap.set_ylabel("Accuracy − Threshold")
ax_gap.set_title(f"Gap to Threshold ({thr})", fontweight="bold")
ax_gap.set_ylim(-0.28, 0.05)
ax_gap.legend(fontsize=9, framealpha=0.7)

# Row 1 far right: retrain rate
ax_ret = fig.add_subplot(gs[1, 3])
pipeline = df[df["retrain_count"] == 0].copy()
pipeline["retrained"] = ~pipeline["registered"]
by_c = pipeline.groupby(["dataset_size", "feature_version"])["retrained"].mean() * 100
x = np.arange(len(SIZES))
for i, fv in enumerate(FVS):
    vals = [by_c.get((sz, fv), 0) for sz in SIZES]
    bars = ax_ret.bar(x + (i - 0.5) * 0.35, vals, 0.35,
                      color=COLORS[fv], label=f"Feature {fv}",
                      edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, vals):
        ax_ret.text(bar.get_x() + bar.get_width() / 2, v + 1,
                    f"{v:.0f}%", ha="center", va="bottom", fontsize=8)
ax_ret.set_xticks(x)
ax_ret.set_xticklabels(SIZE_LABELS, fontsize=9)
ax_ret.set_ylabel("Retrain trigger rate (%)")
ax_ret.set_title("Auto-Retrain Rate", fontweight="bold")
ax_ret.set_ylim(0, 115)
ax_ret.legend(fontsize=9, framealpha=0.7)

out = RESULTS / "combined.png"
fig.savefig(out, bbox_inches="tight")
print(f"saved → {out}")
plt.close(fig)

print(f"\nAll charts saved to {RESULTS}")
