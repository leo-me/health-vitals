import enum
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AuthType(enum.Enum):
  JWT = "jwt"
  API_KEY = "api_key"


class ConsumerConfig(BaseModel):
  output_format: str = 'json'
  data_frequency: int = 10
  endpoint_url: str = 'http://localhost:8001'
  auth: AuthType = AuthType.JWT


class Settings(BaseSettings):
  smart_watch: ConsumerConfig
  web_dashboard: ConsumerConfig
  researcher: ConsumerConfig
  ml: ConsumerConfig


settings = Settings(
  smart_watch=ConsumerConfig(
    output_format='json',
    data_frequency=5*1000, # every 5 seconds
    endpoint_url= '',
    auth=AuthType.JWT
  ),
  web_dashboard=ConsumerConfig(
    output_format='json',
    data_frequency=1000, # every seconds
    endpoint_url='',
    auth=AuthType.JWT
  ),
  researcher=ConsumerConfig(
    output_format='csv',
    data_frequency=10*60*1000, # every 10 mins
    endpoint_url='',
    auth=AuthType.JWT
  ),
  ml=ConsumerConfig(
    output_format='json',
    data_frequency=60*1000, # every mins
    endpoint_url='',
    auth=AuthType.API_KEY
  )
)






