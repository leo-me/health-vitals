# Experiment 2 — MLflow Model Registry Pipeline
## Result Report

---

## 1. Experiment Overview

This experiment validates the end-to-end ML pipeline lifecycle for the Sensors2Care system. The pipeline covers synthetic sensor data generation, feature engineering, model training, threshold-based registration, and automatic retraining on failure. All runs are tracked and versioned in MLflow.

**Research question:** Does the pipeline correctly enforce registration thresholds and trigger automatic retraining, and how do dataset size and feature engineering affect model accuracy and training time?

> **Note on thresholds.** An earlier iteration of this experiment used thresholds `{0.75, 0.80, 0.85}`, against which **every** run failed because the synthetic dataset has no learnable signal (features and labels are sampled independently — see §5). To exercise *both* the registration branch and the retrain branch of the pipeline, thresholds were lowered to `{0.50, 0.55, 0.60}`, which bracket the empirical majority-class baseline (~0.55–0.59). The numbers below correspond to this lowered set.

---

## 2. Parameter Design

### 2.1 Experimental Matrix

| Dimension | Values | Count |
|-----------|--------|-------|
| Dataset sizes | 1 000 (small), 50 000 (medium), 500 000 (large) | 3 |
| Accuracy thresholds | **0.50, 0.55, 0.60** | 3 |
| Feature versions | v1 (raw), v2 (raw + rolling statistics) | 2 |
| Scenarios | Standard (clean), Forced-fail (Gaussian noise injected) | 2 |
| **Total pipeline calls** | 3 × 3 × 2 × 2 = **36** | |
| **Total MLflow runs** | 36 initial + 13 retrains = **49** | |

### 2.2 Dataset Generation

Synthetic sensor feature vectors drawn from distributions matching Empatica E4 statistical properties:

| Signal | Distribution | Sampling rate |
|--------|-------------|---------------|
| EDA | Normal(μ=2.5, σ=1.2), clipped ≥ 0 | 4 Hz |
| BVP | Normal(μ=65, σ=8) | 64 Hz |
| ACC | Normal(μ=0.02, σ=0.15) | 32 Hz |
| IBI | Normal(μ=0.85, σ=0.12), clipped ≥ 0.3 | ~1 Hz (event) |

Stress label: binary (0 = no stress, 1 = stress), class ratio 40 % / 60 %. Each row represents one aggregated time window. **Labels are sampled independently of features**, so the optimal classifier reduces to "predict the majority class" with theoretical ceiling ≈ 0.60.

### 2.3 Feature Engineering

| Version | Features | Dimensionality |
|---------|----------|---------------|
| v1 | Raw EDA, BVP, ACC, IBI | 4 |
| v2 | v1 + rolling mean and std (window = 10) for each signal | 12 |

### 2.4 Model and Training

| Parameter | Value |
|-----------|-------|
| Classifier | RandomForestClassifier |
| n_estimators | 100 |
| Train / test split | 80 % / 20 %, stratified by random_state |
| Initial random_state | 42 |
| Retrain random_state | 142 (initial + 100) |

### 2.5 Registration Logic

```
accuracy >= threshold  →  register model, tag status=production
accuracy <  threshold  →  log FAILED, retrain once (random_state + 100)
                          retrain result logged regardless of outcome
```

### 2.6 Forced-fail Scenario

Gaussian noise N(0, 5) is added to all feature columns before training to verify that the pipeline correctly detects failures and triggers the retrain branch even when threshold conditions would otherwise be borderline.

---

## 3. Metrics

| Metric | Definition | Logged in |
|--------|-----------|-----------|
| `accuracy` | Fraction of correctly classified test samples | MLflow metric |
| `duration_seconds` | Wall-clock training time (fit + predict) | MLflow metric |
| `retrain_count` | 0 = initial attempt, 1 = automatic retrain | MLflow metric |
| `registration_status` | `"registered"` or `"failed"` | MLflow param |
| `registered` | Boolean derived from registration_status | CSV export |
| `force_fail` | Whether noise injection was applied | MLflow param |

---

## 4. Results

### 4.1 Registration Summary

| Metric | Value |
|--------|-------|
| Total pipeline calls | 36 |
| Total MLflow runs logged | 49 (36 initial + 13 retrains) |
| **Initial-attempt registrations** | **23 / 36 (63.9 %)** |
| **Retrain triggered** | **13 / 36 (36.1 %)** |
| Of which retrain succeeded | 1 / 13 |
| **Final registrations after retrain** | **24 / 36 (66.7 %)** |

The three thresholds were chosen to span the empirical accuracy band, so the matrix exercises all three pipeline states:

| Threshold | Initial pass-rate | Branch exercised |
|---|---|---|
| 0.50 | 12 / 12 (100 %) | Always registers — confirms happy-path |
| 0.55 | 11 / 12 (91.7 %) | Boundary — 1 retrain triggered, which then registered |
| 0.60 | 0 / 12 (0 %) | Always fails — confirms retrain branch, retrain also fails (baseline < 0.60) |

This is the design intent: at thr=0.50 the gate lets everything through, at thr=0.55 it sits on top of the baseline so outcomes flip individually, and at thr=0.60 nothing crosses, so both the initial-fail logging and the retrain branch fire on every call.

### 4.2 Accuracy by Dataset Size and Feature Version

#### Standard scenario (clean data, initial attempt)

| Dataset size | Feature v1 (mean) | Feature v2 (mean) | Gap to thr=0.50 (v2) |
|---|---|---|---|
| small (1 K)   | 0.570 | 0.546 | +0.046 |
| medium (50 K) | 0.559 | 0.590 | +0.090 |
| large (500 K) | 0.564 | 0.588 | +0.088 |

#### Forced-fail scenario (noise injected, initial attempt)

| Dataset size | Feature v1 (mean) | Feature v2 (mean) | Gap to thr=0.50 (v2) |
|---|---|---|---|
| small (1 K)   | 0.555 | 0.551 | +0.051 |
| medium (50 K) | 0.559 | 0.594 | +0.094 |
| large (500 K) | 0.563 | 0.588 | +0.088 |

**Key observation — "Gap to Threshold" is *not* model skill.** Gaps land in `+0.046 … +0.094`, which is exactly the offset between the **majority-class baseline (≈0.55–0.59)** and the lowered threshold (0.50). The classifier has not learned a discriminative mapping; it is essentially predicting the majority class. The same gap analysis explains why every run at thr=0.60 fails (baseline < 0.60) and why a single thr=0.55 run flipped from fail to pass on retrain (random-state jitter at the baseline boundary).

### 4.3 Feature Version Comparison

| Feature version | Mean accuracy | Std |
|---|---|---|
| v1 (raw) | 0.562 | 0.011 |
| v2 (raw + rolling stats) | 0.575 | 0.022 |

Feature v2 yields a ~+0.013 improvement over v1. The direction is consistent with the prior experiment (+0.017), and is best read as a small, mostly-noise fluctuation around the majority baseline rather than evidence of real feature gain — the rolling statistics are computed over the same independent-of-label features, so they cannot inject signal that the raw columns do not contain.

### 4.4 Effect of Dataset Size on Accuracy

Accuracy varies by less than 0.03 across all three dataset sizes for both feature versions. Increasing data from 1 K to 500 K rows does not improve the classifier because the synthetic labels are independent of the features — there is no latent signal to extract regardless of sample count. Variance shrinks with N (1 K std ≈ 0.020 → 500 K std ≈ 0.0007), which is the expected √N behavior but does not move the mean.

### 4.5 Training Duration

| Dataset size | Feature v1 (mean) | Feature v2 (mean) | v2 overhead |
|---|---|---|---|
| small (1 K)   | 0.14 s | 0.18 s | +23 % |
| medium (50 K) | 15.8 s | 17.9 s | +14 % |
| large (500 K) | 257 s (4.3 m) | 294 s (4.9 m) | +14 % |

Training time scales approximately linearly with dataset size. Feature v2 adds ~14–23 % overhead due to the rolling-window computation over the larger feature matrix.

### 4.6 Scenario Comparison (Standard vs Forced-fail)

| Scenario | Mean accuracy | Std |
|---|---|---|
| Standard    | 0.570 | 0.018 |
| Forced-fail | 0.568 | 0.020 |

The difference is statistically negligible (Δ = 0.002). Noise injection at σ=5 does not meaningfully degrade accuracy below its already-baseline floor — there is no signal for the noise to drown out.

---

## 5. Discussion

The core finding is unchanged from the high-threshold iteration: **the MLflow pipeline infrastructure operates correctly**, while **the synthetic dataset has no learnable signal**, so all accuracy results cluster around the majority-class baseline (~0.55–0.59 for 60 % stress-label prevalence).

What changed by lowering the thresholds is the *coverage of pipeline states exercised*:

- The **register branch** (`accuracy >= threshold` → log model + tag `status=production`) now actually fires (24 successful registrations); the high-threshold version never executed it.
- The **retrain branch** still fires on every call where the threshold sits above the baseline (12 calls at thr=0.60, plus 1 at thr=0.55).
- The **boundary case at thr=0.55** demonstrates that retrain can flip an outcome: one forced-fail run at (size=1K, fv=v2) initially logged accuracy=0.535 (fail), then retrained at random_state=142 to accuracy=0.575 (pass) — exactly the kind of "marginal fail that a retrain can rescue" the gate is designed to handle.
- The **MLflow tracking** captured all 49 runs (params, metrics, model artifacts, retrain lineage), demonstrating the observability properties of the registry.
- The **computational cost** of the pipeline is predictable: ~5 minutes for 500 K rows at n_estimators=100.

**Caveat on interpretation.** A passing registration in this experiment does *not* imply the model is useful — it only proves the gate machinery works. The accuracy ≈ 0.55–0.59 reflects the data, not the classifier. To demonstrate genuine model quality crossing a threshold, one would either inject a real feature → label dependency into the generator, or replace the synthetic labels with the physiological stress labels from the Empatica E4 dataset (loaded via `data/pipelines/load_subjects.py`).

---

## 结论（中文）

### 实验目标

本实验验证了 Sensors2Care 系统的完整 ML Pipeline 生命周期：合成传感器数据生成 → 特征工程 → 模型训练 → 基于阈值的注册决策 → 自动重训机制。所有运行均通过 MLflow 追踪与版本管理。

### 阈值选择说明

初版实验使用 `{0.75, 0.80, 0.85}` 三个阈值，导致 36 次 Pipeline 全部失败（合成数据无可学信号，准确率天花板≈0.60）。为完整覆盖 Pipeline 的**注册分支**与**重训分支**，阈值改为 `{0.50, 0.55, 0.60}`，正好分别落在多数类基线（≈0.55–0.59）的下方、之内、上方，从而让三种 Pipeline 状态都被触发。下文数值对应新的阈值集合。

### 参数与设计

实验矩阵为 3 个数据集规模 × 3 个准确率阈值 × 2 个特征版本 × 2 个场景，共 36 次 Pipeline 调用，产生 49 条 MLflow 运行记录（36 次初始 + 13 次重训）。

特征版本：v1 使用 EDA、BVP、ACC、IBI 四路原始信号；v2 在 v1 基础上追加窗口为 10 的滚动均值与标准差，特征维度从 4 扩展至 12。分类器为 RandomForestClassifier（n_estimators=100），训练/测试比例为 8:2。

### 实验结果

**注册结果（新阈值）：**

| 阈值 | 初次通过率 | 触发的分支 |
|---|---|---|
| 0.50 | 12 / 12（100%） | 注册分支——确认 happy-path |
| 0.55 | 11 / 12（91.7%） | 边界——触发 1 次重训，重训成功 |
| 0.60 | 0 / 12（0%）    | 失败分支——12 次重训全部仍未达标 |

**最终注册率 24 / 36 = 66.7%。**

**Gap to Threshold 的含义需谨慎解读。** 所有 Gap 值落在 `+0.046 ~ +0.094`，正好等于"多数类基线（≈0.55–0.59）− 阈值 0.50"。这并不意味着模型学到了判别力——由于合成数据中特征与标签独立采样，分类器只能近似预测多数类，准确率天花板约 0.60。在 thr=0.60 时所有 Pipeline 失败、在 thr=0.55 边界处个别样本随重训翻转，都是同一现象在不同阈值下的体现。

**特征工程效果：** v2 相比 v1 平均准确率提升约 0.013（0.562 → 0.575），变化方向与初版实验一致，但本质仍属基线附近的噪声波动而非真实信号增益。

**数据规模影响：** 从 1K 增至 500K 条样本，准确率均值变化不超过 0.03，方差按 √N 缩小（1K std ≈ 0.020 → 500K std ≈ 0.0007），印证"无信号数据增加样本量无益"。

**训练时长：** 随数据量线性扩展——small ~0.15s，medium ~17s，large ~275s。v2 因特征矩阵更大，耗时增加约 14–23%。

**Forced-fail 场景：** 注入 σ=5 高斯噪声后与标准场景准确率差异仅为 0.002，可忽略——数据已无信号，额外噪声无可降级的空间。

### 结论意义

本实验的核心价值在于 **Pipeline 基础设施的可验证性**：通过将阈值下调至跨越多数类基线两侧，36 次调用完整覆盖了"通过 / 边界 / 失败"三种状态——注册分支、重训分支、MLflow 追踪与模型版本标签均按设计执行。**注意：注册通过并不代表模型有效**，accuracy ≈ 0.55–0.59 反映的是数据本身（合成标签与特征独立），而非分类器性能。要让"通过阈值"具有模型质量含义，需将合成标签替换为从 Empatica E4 真实数据（`data/pipelines/load_subjects.py` 加载）提取的生理应力标签，让特征与标签建立真实统计关系。

---

## 7. Re-run via backend HTTP API (2026-05-25)

The pipeline above ran directly inside `run_pipeline.py` (in-process sklearn + MLflow client). On **2026-05-25** the experiment was rewired so that **every step is reached by hitting the backend's `POST /api/v1/train/` endpoint** — synthetic data generation, feature engineering, training, MLflow logging, and the PG dual-write into `model_version` + `model_registry` all happen inside the production code path.

### 7.1 Architecture used

```
run_all.py → api_client.py ──HTTP──▶ backend /api/v1/train (admin-only, BackgroundTask)
                                          ├─▶ feature_service.build_dataset(simulation)
                                          ├─▶ training_service.run_training (+force_fail noise)
                                          ├─▶ MLflow runs / Model Registry (localhost:5004)
                                          └─▶ PostgreSQL: model_version + model_registry
```

Notable shifts vs. §5 above:

| Aspect | Original (in-process) | HTTP-driven (this section) |
|---|---|---|
| Caller | `run_pipeline.run_pipeline(df, …)` | `httpx.post("/api/v1/train")` + poll `GET /train/{job_id}` |
| Auth | none | JWT for a seeded admin (alembic `150a555cf5a9`) |
| Synthetic data | local `generate_data.py` | backend `feature_service._generate_synthetic` |
| Noise injection (force_fail) | inside `run_pipeline.py` | inside `training_service.run_training` (between `build_dataset` and `train_test_split`) |
| `status=production` MLflow tag | yes | replaced by `model_registry.stage = 'PRODUCTION'` in PG (and previous rows auto-flipped to `ARCHIVED`) |

### 7.2 Matrix executed

Reduced sweep used: **2 sizes × 3 thresholds × 2 fv × 2 scenarios = 24 pipeline calls**. The `large` (500 000-row) cell was skipped because each force-fail large run takes ~8 min, bringing the full sweep above 1 h 50 min — an HTTP refactor is not the right test bed to confirm scaling cost.

### 7.3 Results — cleaned matrix (last run per cell)

The MLflow store carried a few stale runs from earlier sanity checks; the figures below come from `results/pipeline_results_clean.csv`, which keeps only the most recent run per `(force_fail, dataset_size, threshold, feature_version, retrain_count)` cell.

| Scenario × size | runs | registered | retrained | mean acc | mean dur (s) |
|---|---:|---:|---:|---:|---:|
| standard × 1 000 | 8 | 4 | 2 | 0.5581 | 0.22 |
| standard × 50 000 | 8 | 4 | 2 | 0.5721 | 21.01 |
| forced_fail × 1 000 | 9 | 4 | 3 | 0.5528 | 0.18 |
| forced_fail × 50 000 | 8 | 4 | 2 | 0.5760 | 18.68 |

| Threshold | pipelines | registered share | retrain share |
|---|---:|---:|---:|
| 0.50 | 8 | 100 % | 0 % |
| 0.55 | 9 | 89 % | 11 % |
| 0.60 | 16 | 0 % | 50 % |

The retrain branch is exercised end-to-end: at threshold = 0.55 in the forced-fail / small / v2 cell the first attempt scored 0.525 < 0.55 (fail), the retrain with `random_state + 100` scored 0.575 ≥ 0.55 (pass), and the second attempt's run is the one that actually wrote `model_version` + `model_registry` rows. This is the "fail then rescue" branch of the pipeline that the original in-process run also covered, now reproduced through the HTTP API.

### 7.4 Dual-write verification & mutex-production invariant

After truncating `model_version` + `model_registry` and re-running, PG contained one row per registered pipeline call:

```text
        tbl       | count
 ----------------+-------
  model_registry |    16
  model_version  |    16
```

16 == number of `registered=True` cells in §7.3.

**Stage invariant**: at any instant `COUNT(*) WHERE stage='PRODUCTION' AND model_name='SensorsCarePipeline'` must be ≤ 1, with all prior production rows rotated to `ARCHIVED`. The current state after a forward-validation `/train` call (designed to force one more rotation):

```text
       tbl       |   stage    | count
-----------------+------------+-------
 model_registry  | PRODUCTION |     1
 model_registry  | ARCHIVED   |    16
 model_version   | PRODUCTION |     1
 model_version   | ARCHIVED   |    16
```

> **Cascade detail.** An earlier version of `crud_model_registry._archive_prior_productions` only demoted registry rows, leaving the linked `model_version.stage` columns stuck at `PRODUCTION` (so a snapshot of the DB would show 16 model_versions all marked `PRODUCTION` while only 1 model_registry row was). The CRUD layer was updated to cascade the demotion onto `ModelVersion.id IN (...)` in the same transaction — see `apps/backend/app/crud/crud_model_registry.py:_archive_prior_productions`. Historical rows from before the fix were back-filled with one UPDATE keyed on `model_registry.stage = 'ARCHIVED'`. After the fix, an extra `/train` call was issued and both tables remained at 1 / N, confirming forward rotation behaves correctly.

### 7.5 Issues found and fixed during the re-run

1. **MLflow 3.x DNS-rebinding host-header validation.** Out of the box the MLflow server refuses the docker-network hostname `mlflow:5000` with HTTP 403. Fixed by adding `MLFLOW_SERVER_ALLOWED_HOSTS="mlflow:*,mlflow,localhost:*,localhost,127.0.0.1:*,127.0.0.1"` to the `mlflow` service in `infra/docker-compose.yml`.
2. **`force_fail` semantics drift.** The backend's training_service did not previously support the force_fail scenario and did not log a `force_fail` param. Added the field to `TrainingRequest`, injected the noise in `run_training()` between `build_dataset` and `train_test_split` (covers both train and test — matches the original §2.6 semantics), and added the param to `mlflow.log_params` so `collect_results.py` still reads the correct value.
3. **Admin auth.** The `/train` endpoint is admin-only. Added alembic migration `150a555cf5a9_seed_exp2_admin_user.py` that idempotently seeds `exp2-admin@hv.local` with a known password (configurable via `EXP2_ADMIN_EMAIL` / `EXP2_ADMIN_PASSWORD` env vars). `api_client.py` uses the same defaults so dev "just works".
4. **Mutex-production invariant not fully enforced.** Initially the rotation only ran against `model_registry`; `model_version.stage` was hard-coded to `PRODUCTION` on every insert and never demoted (16 versions all flagged `PRODUCTION` while the registry table cleanly held 1/15). Although user-facing inference reads `model_registry` and so was unaffected, the version table looked stale. Fixed by extending `_archive_prior_productions` to cascade the demotion onto linked `ModelVersion` rows in the same transaction; back-filled historical rows with one UPDATE. See §7.4 for the post-fix snapshot.

### 7.6 Charts

All five charts under `results/` were regenerated from `pipeline_results_clean.csv` on 2026-05-25. `plot_results.py` now auto-prefers the clean CSV when present and auto-detects which dataset sizes were actually run (so the small + medium sweep doesn't draw empty bars where `large` used to sit). The earlier subtitles that asserted "no run crossed any threshold" / "all bars below zero → 0 registrations" were dropped — they had become factually wrong now that the lowered thresholds (0.50/0.55/0.60) bracket the empirical baseline.

| File | Shows |
|---|---|
| `results/combined.png` | 5-panel thesis figure: accuracy by scenario, duration scaling, gap to thr=0.5, auto-retrain rate |
| `results/accuracy_overview.png` | Accuracy bars by size × fv, both scenarios, with thr=0.50/0.55/0.60 dashed lines |
| `results/gap_to_threshold.png` | Three panels (one per threshold) showing accuracy − threshold; positive bars register, negative bars trigger retrain |
| `results/duration_scaling.png` | Mean training duration on log scale: 0.2s small vs ~20s medium |
| `results/retrain_behavior.png` | Percent of pipeline calls per (size, fv) that triggered the retrain branch |

![Combined thesis figure](results/combined.png)

![Accuracy gap to threshold](results/gap_to_threshold.png)
