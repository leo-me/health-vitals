from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.sensor_recording import SensorRecordingResponse, SensorRecordingCreate
from uuid import UUID

from app.crud import crud_sensor_recording as crud
from app.db.session import get_db


router = APIRouter(prefix="/sensor_recordings", tags=["sensor_recording"])




@router.get('/user/{user_id}', response_model=list[SensorRecordingResponse])
def get_sensor_recording_by_user(user_id: UUID, db: Session=Depends(get_db)):
  recordings = crud.get_recordings_by_user(db, user_id)
  if not recordings:
    raise HTTPException(status_code=404, detail='Device not found')
  return recordings


@router.get('/device/{device_id}', response_model=list[SensorRecordingResponse])
def get_sensor_recording_by_device(device_id: UUID, db: Session=Depends(get_db)):
  recordings = crud.get_recordings_by_device(db, device_id)
  if not recordings:
    raise HTTPException(status_code=404, detail='Device not found')
  return recordings

@router.get('/{recording_id}', response_model=SensorRecordingResponse)
def get_sensor_recording(recording_id: UUID, db: Session=Depends(get_db)):
  recording = crud.get_sensor_recording(db, recording_id)
  if not recording:
    raise HTTPException(status_code=404, detail='Device not found')
  return recording


@router.post('/', response_model=SensorRecordingResponse)
def create_sensor_recording(data: SensorRecordingCreate, db: Session=Depends(get_db)):
  return crud.create_sensor_recording(db, data)


















# POST   /sensor-recordings/                        创建记录
# GET    /sensor-recordings/{recording_id}          查询单条
# GET    /sensor-recordings/user/{user_id}          按用户查
# GET    /sensor-recordings/device/{device_id}      按设备查


