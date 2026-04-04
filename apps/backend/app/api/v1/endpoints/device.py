from uuid import UUID
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.device import DeviceResponse, DeviceCreate, DeviceUpdate
from app.crud import crud_device as crud
from app.db.session import get_db


router = APIRouter(prefix="/device", tags=["device"])


@router.get('/{device_id}', response_model=DeviceResponse)
def get_device(device_id: UUID, db: Session=Depends(get_db)):
  device = crud.get_device(db, device_id)
  if not device:
    raise HTTPException(status_code=404, detail='Device not found')
  return device

@router.get('/user/{user_id}', response_model=list[DeviceResponse])
def get_device(user_id: UUID, db: Session=Depends(get_db)):
  device = crud.get_devices_by_user(db, user_id)
  if not device:
    raise HTTPException(status_code=404, detail='Device not found')
  return device


@router.post("/", response_model=DeviceResponse)
def create_device(data: DeviceCreate, db: Session=Depends(get_db)):
    try:
      return crud.create_device(db, data)
    except ValueError as e:
      raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{device_id}", response_model=DeviceResponse)
def update_device(device_id: UUID, data: DeviceUpdate, db: Session=Depends(get_db)):
  device = crud.update_device(db, device_id, data)
  if not device:
    raise HTTPException(status_code=404, detail='Device not found')
  return device

@router.delete("/{device_id}")
def delete_device(device_id: UUID, db: Session=Depends(get_db)):
  success = crud.delete_device(db, device_id)
  if not success:
    raise HTTPException(status_code=404, detail='Device not found')
  return {"message": 'Device deleted'}