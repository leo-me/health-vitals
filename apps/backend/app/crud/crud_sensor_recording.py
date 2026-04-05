from datetime import datetime
from uuid import UUID
from app.models.sensor_recording import SensorRecording, SensorType
from app.schemas.sensor_recording import SensorRecordingCreate


from sqlalchemy.orm import Session




def create_sensor_recording(db: Session, data: SensorRecordingCreate) -> SensorRecording:
  recording = SensorRecording(**data.model_dump(exclude_none=True))
  db.add(recording)
  db.commit()
  db.refresh(recording)
  return recording



def get_sensor_recording(db: Session, recording_id: UUID) -> SensorRecording:
  return db.query(SensorRecording).filter(SensorRecording.id == recording_id).first()



def get_recordings_by_user(
  db: Session,
  user_id: UUID,
  start: datetime | None = None,
  end: datetime | None = None,
  page: int = 1,
  page_size: int  = 10,
  sensor_type: SensorType | None = None
)  -> list[SensorRecording]: #← search by user and return list
  query =  db.query(SensorRecording).filter(SensorRecording.user_id == user_id)

  if sensor_type is not None:
    query = query.filter(SensorRecording.sensor_type == sensor_type)

  if start is not None:
    query = query.filter(SensorRecording.timestamp >= start)

  if end is not None:
    query = query.filter(SensorRecording.timestamp <= end)

  results = query.offset((page - 1)*page_size).limit(page_size).all()

  return results



def get_recordings_by_device(db: Session, device_id: UUID) ->list[SensorRecording]:    #← search by device and return list
  return db.query(SensorRecording).filter(SensorRecording.device_id == device_id).all()

