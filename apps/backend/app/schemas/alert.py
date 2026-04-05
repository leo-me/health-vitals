# schemas/alert.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AlertCreate(BaseModel):
  recording_id: UUID
  user_id: UUID
  content: str



class AlertResponse(BaseModel): # add model_config
  id: UUID
  user_id: UUID
  content: str
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


