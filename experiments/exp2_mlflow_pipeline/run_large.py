"""
run_large.py —补跑 large (500K) × 3 thresholds × v1 的 3 个缺失 cell。
small 和 medium 已在 pipeline_results_clean.csv 中，不重复跑。
"""

import time
from api_client import login, trigger_training, wait_for_result

THRESHOLDS      = [0.50, 0.55, 0.60]
FEATURE_VERSION = "v1"
DATASET_SIZE    = 400_000


def run_large():
    token   = login()
    total   = len(THRESHOLDS)

    for idx, threshold in enumerate(THRESHOLDS, 1):
        print(f"\n[{idx}/{total}] size=large thr={threshold} fv={FEATURE_VERSION}")
        t0 = time.time()

        job_id = trigger_training(
            token,
            threshold=threshold,
            dataset_size=DATASET_SIZE,
            feature_version=FEATURE_VERSION,
            force_fail=False,
        )
        job = wait_for_result(token, job_id)

        if job["status"] != "succeeded":
            print(f"  ✗ job {job_id} error: {job.get('error')}")
            continue

        result = job["result"]
        status = "REGISTERED" if result["registered"] else "failed"
        elapsed = time.time() - t0
        print(
            f"  → acc={result['accuracy']:.4f}  {status}"
            f"  retrain={result['retrain_count']}"
            f"  ({elapsed:.1f}s)"
        )

    print("\nLarge runs done. Run collect_results.py to update CSV.")


if __name__ == "__main__":
    run_large()
