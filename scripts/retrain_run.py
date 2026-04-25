# retrain_run.py
# Retrains the model using combined original + feedback-corrected data
# Validates that performance recovers after retraining

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

# --- Reproduce original data ---
X, y = make_classification(n_samples=200, n_features=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Simulate feedback data collected from nurses ---
# New labeled samples added after nurse corrections
# This represents the retraining pipeline incorporating user feedback (S7)
X_feedback, y_feedback = make_classification(n_samples=50, n_features=5, random_state=99)

# --- Combine original training data with feedback data ---
X_retrain = np.vstack([X_train, X_feedback])
y_retrain = np.hstack([y_train, y_feedback])

with mlflow.start_run(run_name="retrained"):

    # Train new model on combined dataset
    retrained_model = LogisticRegression()
    retrained_model.fit(X_retrain, y_retrain)

    # Evaluate on original clean test set
    y_pred = retrained_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)

    # Log parameters
    mlflow.log_param("threshold", PERFORMANCE_THRESHOLD)
    mlflow.log_param("retrain_data_size", len(X_retrain))
    mlflow.log_param("feedback_samples", len(X_feedback))

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("below_threshold", int(accuracy < PERFORMANCE_THRESHOLD))

    # Save retrained model to MLflow Model Registry
    mlflow.sklearn.log_model(
        sk_model=retrained_model,
        artifact_path="model",
        registered_model_name="stress-model"  # New version will be created automatically
    )

    print(f"[Retrained] Accuracy: {accuracy:.2f}, Below threshold: {accuracy < PERFORMANCE_THRESHOLD}")

    if accuracy >= PERFORMANCE_THRESHOLD:
        print(">> Model recovered. Ready to promote to Production.")
    else:
        print(">> Model still below threshold. Further investigation needed.")