from uuid import UUID

from sqlalchemy.orm import Session

from sqlalchemy.dialects.postgresql import insert

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate



def get_device(db: Session, device_id: UUID) -> Device | None:
  return db.query(Device).filter(Device.id == device_id).first()

def get_device_serial_no(db: Session, serial_number: UUID) -> Device | None:
  return db.query(Device).filter(Device.serial_number == serial_number).first()

# def create_device(db: Session, data: DeviceCreate) -> Device:
#   existing = get_device_serial_no(db, data.serial_number)
#   if existing:
#     raise ValueError("Serial number already registered")

#   device = Device(**data.model_dump(exclude_none=True))
#   db.add(device)
#   db.commit()
#   db.refresh(device)
#   return device


def update_device(db: Session, device_id: UUID, data: DeviceUpdate) -> Device | None:
  device = get_device(db, device_id)

  if not device:
    return None
  for key, val in data.model_dump(exclude_none=True).items():
    setattr(device, key, val)
  db.commit()
  db.refresh(device)

  return device

def delete_device(db: Session, device_id: UUID) -> bool:
  device = get_device(db, device_id)
  if not device:
    return False
  db.delete(device)
  db.commit()

  return True


def get_devices_by_user(db: Session, user_id: UUID) -> list[Device]:
  return db.query(Device).filter(Device.user_id == user_id).all()


def upsert_device(db: Session, data: DeviceCreate):
    device = data.model_dump(exclude_none=True)

    stmt = insert(Device).values(device) # build sql

    update_fields = {k:v for k, v in device.items() if k not in ('id', 'serial_number')}

    stmt = stmt.on_conflict_do_update(
      index_elements=["serial_number"],
      set_=update_fields
    ).returning(Device)

    result = db.execute(stmt)
    db.commit()
    return result.scalars().first()





