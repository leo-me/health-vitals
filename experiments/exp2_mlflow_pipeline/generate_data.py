"""
Generate synthetic sensor datasets matching EmpaticaE4Stress statistical properties.

Signal properties (per spec):
    EDA  : mean=2.5,  std=1.2  @ 4  Hz
    BVP  : mean=65,   std=8    @ 64 Hz
    ACC  : mean=0.02, std=0.15 @ 32 Hz
    IBI  : mean=0.85, std=0.12 (event-based ~1 Hz)

Each row is a feature vector (one time window), not a raw sample.
Stress label: 60% stress (1), 40% non-stress (0).
"""

import numpy as np
import pandas as pd


DATASET_SIZES = {"small": 1_000, "medium": 50_000, "large": 500_000}


def generate_dataset(size: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    labels = rng.choice([0, 1], size=size, p=[0.4, 0.6])

    eda = rng.normal(2.5,  1.2,  size).clip(0)
    bvp = rng.normal(65,   8,    size)
    acc = rng.normal(0.02, 0.15, size)
    ibi = rng.normal(0.85, 0.12, size).clip(0.3)

    return pd.DataFrame({"eda": eda, "bvp": bvp, "acc": acc, "ibi": ibi, "label": labels})


if __name__ == "__main__":
    for name, n in DATASET_SIZES.items():
        df = generate_dataset(n)
        print(f"{name:8s} ({n:>7,} rows) — stress ratio: {df['label'].mean():.2%}")
