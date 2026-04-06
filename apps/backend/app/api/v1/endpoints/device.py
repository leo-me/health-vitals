from uuid import UUID
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.device import DeviceResponse, DeviceCreate, DeviceUpdate
from app.crud import crud_device as crud
from app.db.session import get_db

from app.models.user import User, UserTypeEnum
from app.dependencies import get_current_user


router = APIRouter(prefix="/device", tags=["device"])


@router.get('/{device_id}', response_model=DeviceResponse)
def get_device(
  device_id: UUID,
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
):
  device = crud.get_device(db, device_id)

  if not device:
    raise HTTPException(status_code=404, detail='Device not found')
  elif current_user.id != device.user_id and current_user.user_type != UserTypeEnum.ADMIN:
    raise HTTPException(status_code=403, detail="No permission")

  return device

@router.get('/user/{user_id}', response_model=list[DeviceResponse])
def get_devices_by_user(
  user_id: UUID,
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
):
  if current_user.id != user_id and current_user.user_type != UserTypeEnum.ADMIN:
    raise HTTPException(status_code=403, detail="No permission")

  device = crud.get_devices_by_user(db, user_id)

  if not device:
    raise HTTPException(status_code=404, detail='Device not found')

  return device


@router.post("/", response_model=DeviceResponse)
def register_device(
  data: DeviceCreate,
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
):
  if current_user.user_type == UserTypeEnum.ADMIN:
    data.user_id = current_user.id

  return crud.upsert_device(db, data)



@router.patch("/{device_id}", response_model=DeviceResponse)
def update_device(
  device_id: UUID,
  data: DeviceUpdate,
  current_user: User=Depends(get_current_user),
  db: Session=Depends(get_db)
):
  device = crud.update_device(db, device_id, data)
  if not device:
    raise HTTPException(status_code=404, detail='Device not found')
  return device

@router.delete("/{device_id}")
def delete_device(device_id: UUID, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
  success = crud.delete_device(db, device_id)
  if not success:
    raise HTTPException(status_code=404, detail='Device not found')
  return {"message": 'Device deleted'}