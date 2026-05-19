import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str
  SECURITY_KEY: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  ALGORITHM: str
  MLFLOW_TRACKING_URI: str = "http://localhost:5004"
  MLFLOW_EXPERIMENT: str = "sensors2care_registry"
  MLFLOW_MODEL_NAME: str = "SensorsCarePipeline"

  @property
  def database_url(self) -> str:
    return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

  class Config:
    env_file = os.getenv("ENV_FILE", ".env")



settings = Settings()