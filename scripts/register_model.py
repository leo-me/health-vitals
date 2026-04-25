import mlflow
import mlflow.sklearn
from sklearn.dummy import DummyClassifier

mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("stress-detection")

with mlflow.start_run():
    model = DummyClassifier()
    model.fit([[0]], [0])

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="stress-model"
    )