# schemas/device.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

from app.models.device import DeviceType



class DeviceCreate(BaseModel):
  user_id: Optional[UUID] = None
  type: DeviceType
  push_token: Optional[str] = None
  serial_number: Optional[str] = None


class DeviceResponse(BaseModel):
  id: UUID
  user_id: Optional[UUID] = None
  type: DeviceType
  created_at: datetime
  model_config=ConfigDict(from_attributes=True)
  serial_number: Optional[str] = None

class DeviceAdminResponse(BaseModel):     # admin，include push_token
    id: UUID
    user_id: Optional[UUID] = None
    type: DeviceType
    push_token: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    serial_number: Optional[str] = None

class DeviceUpdate(BaseModel):
  user_id: Optional[UUID] = None
  type: Optional[DeviceType] = None
  push_token: Optional[str] = None
  serial_number: Optional[str] = None

