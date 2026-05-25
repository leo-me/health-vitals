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

  # Seeded by migration `seed_exp2_admin_user`. exp2's HTTP client also reads
  # these (via the env file or its own defaults) to log in against /train.
  # Heads-up: users.email is varchar(30) — pick a value that fits.
  EXP2_ADMIN_EMAIL: str    = "exp2-admin@hv.local"
  EXP2_ADMIN_PASSWORD: str = "exp2-admin-changeme"

  @property
  def database_url(self) -> str:
    return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

  class Config:
    env_file = os.getenv("ENV_FILE", ".env")



settings = Settings()