from uuid import UUID
from app.models.sensor_recording import SensorRecording
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



def get_recordings_by_user(db: Session, user_id: UUID)  -> list[SensorRecording]: #← 按用户查，返回列表
  return db.query(SensorRecording).filter(SensorRecording.user_id == user_id).all()

def get_recordings_by_device(db: Session, device_id: UUID) ->list[SensorRecording]:    #← 按设备查，返回
  return db.query(SensorRecording).filter(SensorRecording.device_id == device_id).all()

