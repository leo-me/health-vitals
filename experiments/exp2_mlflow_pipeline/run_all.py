"""
run_all.py — execute the 9-run matrix through the backend /train HTTP API.

New design (no forced_fail, no feature-version sweep):
    Matrix: 3 dataset sizes × 3 thresholds × feature_version=v1 = 9 pipeline calls
    Scenario: standard (clean data) only — threshold level controls pass/fail naturally:
        threshold=0.50 → always registers  (below baseline floor)
        threshold=0.55 → boundary          (retrain may flip outcome)
        threshold=0.60 → always fails      (above baseline ceiling ≈ 0.60)

Each failed initial run triggers one automatic retrain (random_state + 100), so
total MLflow runs can reach up to 18 (9 initial + up to 9 retrains).
"""

import time

from api_client import login, trigger_training, wait_for_result

DATASET_SIZES = {
    "small":  1_000,
    "medium": 50_000,
    "large":  400_000,   # 500K OOMs in Docker VM (7.666 GiB); 400K is the boundary tested
}

THRESHOLDS      = [0.50, 0.55, 0.60]
FEATURE_VERSION = "v1"


def run_all():
    token   = login()
    results = []
    runs    = [(name, size, thr)
               for name, size in DATASET_SIZES.items()
               for thr in THRESHOLDS]
    total   = len(runs)

    for idx, (size_name, size, threshold) in enumerate(runs, 1):
        label = f"[{idx}/{total}] size={size_name} thr={threshold} fv={FEATURE_VERSION}"
        print(f"\n{label}")
        t0 = time.time()

        job_id = trigger_training(
            token,
            threshold=threshold,
            dataset_size=size,
            feature_version=FEATURE_VERSION,
            force_fail=False,
        )
        job = wait_for_result(token, job_id)

        if job["status"] != "succeeded":
            print(f"  ✗ job {job_id} failed: {job.get('error')}")
            continue

        result = job["result"]
        results.append(result)

        status = "REGISTERED" if result["registered"] else "failed"
        print(
            f"  → acc={result['accuracy']:.4f}  {status}"
            f"  retrain={result['retrain_count']}"
            f"  ({time.time()-t0:.1f}s)"
        )

    print(f"\nAll done. {len(results)} pipeline results collected.")
    print("Run collect_results.py to export to CSV.")
    return results


if __name__ == "__main__":
    run_all()
