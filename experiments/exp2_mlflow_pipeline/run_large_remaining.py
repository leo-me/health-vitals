"""补跑 400K × thr=0.55 和 thr=0.60（thr=0.50 已完成）"""
import time
from api_client import login, trigger_training, wait_for_result

for threshold in [0.55, 0.60]:
    token = login()
    print(f"\n[large 400K] thr={threshold}")
    t0 = time.time()
    job_id = trigger_training(token, threshold=threshold, dataset_size=400_000,
                              feature_version="v1", force_fail=False)
    job = wait_for_result(token, job_id)
    result = job["result"]
    status = "REGISTERED" if result["registered"] else "failed"
    print(f"  → acc={result['accuracy']:.4f}  {status}  retrain={result['retrain_count']}  ({time.time()-t0:.0f}s)")
