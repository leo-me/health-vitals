"""
run_all.py — execute all 18 standard + 18 forced-fail combinations.

Matrix: 3 dataset sizes × 3 thresholds × 2 feature versions = 18 per scenario
Total MLflow runs logged: up to 72 (each failed run triggers one retrain).
"""

import time

from generate_data import generate_dataset, DATASET_SIZES
from run_pipeline import run_pipeline

THRESHOLDS       = [0.75, 0.80, 0.85]
FEATURE_VERSIONS = ["v1", "v2"]


def run_all():
    results = []
    total   = len(DATASET_SIZES) * len(THRESHOLDS) * len(FEATURE_VERSIONS)
    idx     = 0

    for scenario, force_fail in [("standard", False), ("forced_fail", True)]:
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario}")
        print(f"{'='*60}")

        for size_name, size in DATASET_SIZES.items():
            df = generate_dataset(size)

            for threshold in THRESHOLDS:
                for fv in FEATURE_VERSIONS:
                    idx += 1
                    label = f"[{idx}/{total}] size={size_name} thr={threshold} fv={fv}"
                    print(f"\n{label}  force_fail={force_fail}")
                    t0 = time.time()

                    result = run_pipeline(
                        df,
                        threshold=threshold,
                        dataset_size=size,
                        feature_version=fv,
                        force_fail=force_fail,
                    )
                    result["scenario"] = scenario
                    results.append(result)

                    status = "REGISTERED" if result["registered"] else "failed"
                    print(
                        f"  → acc={result['accuracy']:.4f}  {status}"
                        f"  retrain={result['retrain_count']}"
                        f"  ({time.time()-t0:.1f}s)"
                    )

        idx = 0  # reset counter for second scenario

    print(f"\nAll done. {len(results)} pipeline results collected.")
    print("Run collect_results.py to export to CSV.")
    return results


if __name__ == "__main__":
    run_all()
