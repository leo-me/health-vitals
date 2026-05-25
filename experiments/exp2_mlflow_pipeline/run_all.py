"""
run_all.py — execute all 18 standard + 18 forced-fail combinations through
the backend /train HTTP API.

Matrix: 3 dataset sizes × 3 thresholds × 2 feature versions = 18 per scenario.
Total MLflow runs logged: up to 72 (each failed run triggers one retrain).

Synthetic data generation, feature engineering, sklearn fit, and MLflow
logging all live in the backend now — see app/services/{feature,training}_service.
Inspect the trace by following the architecture diagram in readme.md.
"""

import time

from api_client import login, trigger_training, wait_for_result

# Was previously in generate_data.py; inlined here since generation moved to
# the backend (feature_service._generate_synthetic). "large" (500k) is
# commented out — each large+force_fail run takes ~8 min, blowing the matrix
# to ~2 hours. Uncomment for a fuller sweep when you have the time.
DATASET_SIZES = {
    "small":  1_000,
    "medium": 50_000,
    "large":  500_000,
}

# THRESHOLDS       = [0.75, 0.80, 0.85]
THRESHOLDS       = [0.50, 0.55, 0.60]
FEATURE_VERSIONS = ["v1", "v2"]


def run_all():
    token   = login()  # one JWT for the whole matrix; backend uses 60-min expiry
    results = []
    total   = len(DATASET_SIZES) * len(THRESHOLDS) * len(FEATURE_VERSIONS)
    idx     = 0

    for scenario, force_fail in [("standard", False), ("forced_fail", True)]:
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario}")
        print(f"{'='*60}")

        for size_name, size in DATASET_SIZES.items():
            for threshold in THRESHOLDS:
                for fv in FEATURE_VERSIONS:
                    idx += 1
                    label = f"[{idx}/{total}] size={size_name} thr={threshold} fv={fv}"
                    print(f"\n{label}  force_fail={force_fail}")
                    t0 = time.time()

                    job_id = trigger_training(
                        token,
                        threshold=threshold,
                        dataset_size=size,
                        feature_version=fv,
                        force_fail=force_fail,
                    )
                    job = wait_for_result(token, job_id)

                    if job["status"] != "succeeded":
                        print(f"  ✗ job {job_id} failed: {job.get('error')}")
                        continue

                    result = job["result"]
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
