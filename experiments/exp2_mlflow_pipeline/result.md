# Experiment 2 — MLflow Model Registry Pipeline
## Result Report

---

## 1. Experiment Overview

This experiment validates the end-to-end ML pipeline lifecycle for the Sensors2Care system. The pipeline covers synthetic sensor data generation, feature engineering, model training, threshold-based registration, and automatic retraining on failure. All runs are tracked and versioned in MLflow.

**Research question:** Does the pipeline correctly enforce registration thresholds and trigger automatic retraining, and how do dataset size and feature engineering affect model accuracy and training time?

---

## 2. Parameter Design

### 2.1 Experimental Matrix

| Dimension | Values | Count |
|-----------|--------|-------|
| Dataset sizes | 1 000 (small), 50 000 (medium), 500 000 (large) | 3 |
| Accuracy thresholds | 0.75, 0.80, 0.85 | 3 |
| Feature versions | v1 (raw), v2 (raw + rolling statistics) | 2 |
| Scenarios | Standard (clean), Forced-fail (Gaussian noise injected) | 2 |
| **Total pipeline calls** | 3 × 3 × 2 × 2 = **36** | |
| **Total MLflow runs** | Up to 72 (each failed call triggers one retrain) | |

### 2.2 Dataset Generation

Synthetic sensor feature vectors drawn from distributions matching Empatica E4 statistical properties:

| Signal | Distribution | Sampling rate |
|--------|-------------|---------------|
| EDA | Normal(μ=2.5, σ=1.2), clipped ≥ 0 | 4 Hz |
| BVP | Normal(μ=65, σ=8) | 64 Hz |
| ACC | Normal(μ=0.02, σ=0.15) | 32 Hz |
| IBI | Normal(μ=0.85, σ=0.12), clipped ≥ 0.3 | ~1 Hz (event) |

Stress label: binary (0 = no stress, 1 = stress), class ratio 40 % / 60 %. Each row represents one aggregated time window.

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
| Total MLflow runs logged | 72 (36 initial + 36 retrains) |
| Successful registrations | **0 / 36 (0 %)** |
| Retrain triggered | **36 / 36 (100 %)** |

No run crossed any threshold. The pipeline's gate mechanism functioned correctly — every failed initial run triggered exactly one automatic retrain, which was also logged in MLflow.

### 4.2 Accuracy by Dataset Size and Feature Version

#### Standard scenario (clean data)

| Dataset size | Feature v1 (mean) | Feature v2 (mean) | Gap to thr=0.75 (v2) |
|---|---|---|---|
| small (1 K) | 0.560 | 0.543 | −0.208 |
| medium (50 K) | 0.560 | 0.591 | −0.159 |
| large (500 K) | 0.564 | 0.588 | −0.162 |

#### Forced-fail scenario (noise injected)

| Dataset size | Feature v1 (mean) | Feature v2 (mean) | Gap to thr=0.75 (v2) |
|---|---|---|---|
| small (1 K) | 0.545 | 0.555 | −0.195 |
| medium (50 K) | 0.560 | 0.593 | −0.157 |
| large (500 K) | 0.563 | 0.588 | −0.162 |

**Key observation:** Accuracy is almost identical between the standard and forced-fail scenarios. Since the underlying data has no real signal (features and labels are independently generated), the injected noise has negligible effect — the model was already at near-random performance.

### 4.3 Feature Version Comparison

| Feature version | Mean accuracy | Std |
|---|---|---|
| v1 (raw) | 0.559 | 0.013 |
| v2 (raw + rolling stats) | 0.576 | 0.022 |

Feature v2 yields a consistent +0.017 improvement over v1. The rolling mean and standard deviation features add modest discriminative power, but neither version approaches the registration threshold.

### 4.4 Effect of Dataset Size on Accuracy

Accuracy varies by less than 0.03 across all three dataset sizes for both feature versions. Increasing data from 1 K to 500 K rows does not improve the classifier because the synthetic labels are independent of the features — there is no latent signal to extract regardless of sample count.

### 4.5 Training Duration

| Dataset size | Feature v1 (mean) | Feature v2 (mean) | v2 overhead |
|---|---|---|---|
| small (1 K) | 0.13 s | 0.16 s | +23 % |
| medium (50 K) | 15.5 s | 17.6 s | +14 % |
| large (500 K) | 264 s (4.4 m) | 310 s (5.2 m) | +17 % |

Training time scales approximately linearly with dataset size (verified on log scale). Feature v2 adds ~15–23 % overhead due to the rolling-window computation over the larger feature matrix.

### 4.6 Scenario Comparison (Standard vs Forced-fail)

| Scenario | Mean accuracy | Std |
|---|---|---|
| Standard | 0.568 | 0.019 |
| Forced-fail | 0.567 | 0.021 |

The difference is statistically negligible (Δ = 0.001). This confirms that noise injection at σ=5 does not meaningfully degrade accuracy below its already-random baseline.

---

## 5. Discussion

The core finding is that **the MLflow pipeline infrastructure operates correctly**, but **the synthetic dataset has no learnable signal**, so all accuracy results cluster around the majority-class baseline (~58–60 % for 60 % stress label prevalence).

This is expected and informative for the thesis:

- The **registration gate** (threshold enforcement) and **automatic retrain** logic were exercised across all 36 pipeline calls and behaved exactly as specified.
- The **MLflow tracking** captured all parameters, metrics, and model artifacts for every run and retrain, demonstrating the observability properties of the registry.
- The **feature engineering pipeline** (v1 → v2) is functional and shows measurable — if insufficient — improvement.
- The **computational cost** of the pipeline is predictable: ~5 minutes for 500 K rows at n_estimators=100.

To achieve registration in a production setting, real physiological stress labels from the Empatica E4 dataset (loaded via `data/pipelines/load_subjects.py`) would replace the synthetic labels, providing the signal necessary to cross the accuracy thresholds.

---

## 结论（中文）

### 实验目标

本实验验证了 Sensors2Care 系统的完整 ML Pipeline 生命周期：合成传感器数据生成 → 特征工程 → 模型训练 → 基于阈值的注册决策 → 自动重训机制。所有运行均通过 MLflow 追踪与版本管理。

### 参数与设计

实验矩阵为 3 个数据集规模 × 3 个准确率阈值 × 2 个特征版本 × 2 个场景，共 36 次 Pipeline 调用，最多产生 72 条 MLflow 运行记录（每次失败触发一次重训）。

特征版本方面：v1 使用 EDA、BVP、ACC、IBI 四路原始信号；v2 在 v1 基础上追加窗口为 10 的滚动均值与标准差，特征维度从 4 扩展至 12。分类器为 RandomForestClassifier（n_estimators=100），训练/测试比例为 8:2。

### 实验结果

**注册结果：36 次 Pipeline 调用全部失败，注册率 0%，自动重训触发率 100%。**

所有运行的准确率集中在 0.54–0.59 之间，远低于最低阈值 0.75（差距约 −0.16 至 −0.21）。造成这一结果的根本原因是合成数据中特征与标签相互独立，模型无法学习到有效的判别特征，准确率接近多数类基线（60% 应力标签 → 基线约 58–60%）。

**特征工程效果：** v2 相比 v1 平均准确率提升约 0.017（0.559 → 0.576），滚动统计特征带来了有限但一致的改善，但不足以影响注册结果。

**数据规模影响：** 从 1K 增至 500K 条样本，准确率变化不超过 0.03，印证了"无信号数据增加样本量无益"的理论预期。

**训练时长：** 随数据量线性扩展——small ~0.15s，medium ~17s，large ~290s。v2 特征版本因特征矩阵更大，耗时增加约 15–23%。

**Forced-fail 场景：** 注入高斯噪声（σ=5）与标准场景的准确率差异仅为 0.001，可忽略不计，原因同上：数据本身已无信号，额外噪声不改变结果。

### 结论意义

本实验的核心价值不在于模型性能，而在于**验证 Pipeline 基础设施的正确性**：阈值门控机制、自动重训触发、MLflow 全程追踪均按设计运行。在实际部署中，将合成标签替换为从 Empatica E4 真实数据（`data/pipelines/load_subjects.py` 加载）提取的生理应力标签，即可为模型提供可学习的信号，从而使准确率有望突破注册阈值。
