from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str
  SECURITY_KEY: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  ALGORITHM: str

  class Config:
    env_file = ".env"



settings = Settings()