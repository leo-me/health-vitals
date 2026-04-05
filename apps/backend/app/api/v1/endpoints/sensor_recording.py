from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.sensor_recording import SensorRecordingResponse, SensorRecordingCreate
from app.models.sensor_recording import SensorType

from uuid import UUID

from app.crud import crud_sensor_recording as crud
from app.crud import crud_device
from app.db.session import get_db

from app.services.alert_service import check_and_trigger_alert
from app.models.user import User
from app.dependencies import get_current_user


router = APIRouter(prefix="/sensor_recordings", tags=["sensor_recording"])




@router.get('/user/{user_id}', response_model=list[SensorRecordingResponse])
def get_sensor_recording_by_user(
  user_id: UUID,
  current_user: User=Depends(get_current_user),
  sensor_type: SensorType | None = Query(default=None),
  start: datetime | None = Query(default=None), # like 2026-04-05T00:00:00
  end: datetime | None = Query(default=None),
  page: int = Query(default=1),
  page_size: int = Query(default=10),
  db: Session=Depends(get_db)
  ):
  recordings = crud.get_recordings_by_user(db, user_id, start, end, page, page_size, sensor_type)

  # if not recordings:
  #   raise HTTPException(status_code=404, detail='Recording not found')

  return recordings


@router.get('/device/{device_id}', response_model=list[SensorRecordingResponse])
def get_sensor_recording_by_device(
  device_id: UUID,  
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
):
  recordings = crud.get_recordings_by_device(db, device_id)
  if not recordings:
    raise HTTPException(status_code=404, detail='Recording not found')
  return recordings

@router.get('/{recording_id}', response_model=SensorRecordingResponse)
def get_sensor_recording(
  recording_id: UUID,   
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
 ):
  recording = crud.get_sensor_recording(db, recording_id)
  if not recording:
    raise HTTPException(status_code=404, detail='Recording not found')
  return recording


@router.post('/', response_model=SensorRecordingResponse)
def create_sensor_recording(
  data: SensorRecordingCreate,
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
):
  recording = crud.create_sensor_recording(db, data)

  alert = check_and_trigger_alert(db, recording)

  if alert is not None:

    device = crud_device.get_device(db, recording.device_id)

    if device.push_token is not None:
      # push logic
      pass

  return recording














