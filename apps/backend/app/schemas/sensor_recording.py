# schemas/sensor_recording.py

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


from app.models.sensor_recording import SensorType




class SensorRecordingCreate(BaseModel):
  device_id: UUID
  user_id: UUID
  timestamp: datetime
  sensor_type: SensorType
  data: dict


class SensorRecordingResponse(BaseModel):
  id: UUID
  device_id: UUID
  user_id: UUID
  timestamp: datetime
  sensor_type: SensorType
  data: dict
  created_at: datetime   # ← 加上

  
  model_config = ConfigDict(from_attributes=True)


