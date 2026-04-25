import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("stress-detection")

PERFORMANCE_THRESHOLD = 0.7  # S6/S7 threshold

# 模拟正常数据
X, y = make_classification(n_samples=200, n_features=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

with mlflow.start_run(run_name="baseline"):
    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)

    # log参数
    mlflow.log_param("threshold", PERFORMANCE_THRESHOLD)
    mlflow.log_param("data_size", len(X_train))

    # log指标
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("below_threshold", int(accuracy < PERFORMANCE_THRESHOLD))

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="stress-model"
    )

    print(f"Accuracy: {accuracy:.2f}, Below threshold: {accuracy < PERFORMANCE_THRESHOLD}")