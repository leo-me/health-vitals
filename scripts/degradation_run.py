# degradation_run.py
# Simulates model performance degradation due to data drift and nurse feedback

import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("stress-detection")

PERFORMANCE_THRESHOLD = 0.7

# --- Generate the same baseline data ---
X, y = make_classification(n_samples=200, n_features=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Train the same baseline model ---
baseline_model = LogisticRegression()
baseline_model.fit(X_train, y_train)

# --- Simulate data drift (Phase 2) ---
# Inject Gaussian noise into test data to simulate distribution shift
# This represents real-world sensor data becoming inconsistent over time
noise = np.random.normal(loc=0, scale=2.5, size=X_test.shape)
X_test_drifted = X_test + noise

# --- Simulate nurse feedback ---
# Flip 30% of test labels to simulate incorrect annotations from nurses
# This represents feedback that misleads the model
np.random.seed(0)
flip_indices = np.random.choice(len(y_test), size=int(0.3 * len(y_test)), replace=False)
y_test_noisy = y_test.copy()
y_test_noisy[flip_indices] = 1 - y_test_noisy[flip_indices]

with mlflow.start_run(run_name="degraded"):

    # Evaluate baseline model on drifted + noisy data
    y_pred = baseline_model.predict(X_test_drifted)
    accuracy = accuracy_score(y_test_noisy, y_pred)
    precision = precision_score(y_test_noisy, y_pred, zero_division=0)

    # Log parameters
    mlflow.log_param("threshold", PERFORMANCE_THRESHOLD)
    mlflow.log_param("noise_scale", 2.5)
    mlflow.log_param("feedback_flip_ratio", 0.3)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("below_threshold", int(accuracy < PERFORMANCE_THRESHOLD))

    print(f"[Degraded] Accuracy: {accuracy:.2f}, Below threshold: {accuracy < PERFORMANCE_THRESHOLD}")

    # Trigger retraining if performance is below threshold (corresponds to S6/S7)
    if accuracy < PERFORMANCE_THRESHOLD:
        print(">> Performance below threshold. Retraining should be triggered.")
    else:
        print(">> Performance acceptable. No action needed.")