import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str
  SECURITY_KEY: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  ALGORITHM: str

  @property
  def database_url(self) -> str:
    return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

  class Config:
    env_file = os.getenv("ENV_FILE", ".env")



settings = Settings()