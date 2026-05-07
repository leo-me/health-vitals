import enum
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AuthType(enum.Enum):
  JWT = "jwt"
  API_KEY = "api_key"


class ConsumerConfig(BaseModel):
  output_format: str
  data_frequency: int
  endpoint_url: str
  auth: AuthType


class Settings(BaseSettings):
  smart_watch: ConsumerConfig
  web_dashboard: ConsumerConfig
  researcher: ConsumerConfig
  ml: ConsumerConfig





