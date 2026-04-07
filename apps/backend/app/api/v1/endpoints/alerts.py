from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.alert import AlertResponse, AlertCreate
from app.db.session import get_db
from app.crud import crud_alert  as crud

from app.dependencies import get_current_user
from app.models.user import User, UserTypeEnum



router = APIRouter(prefix="/alert", tags=["alerts"])


@router.get("/user/{user_id}", response_model=list[AlertResponse])
def get_alerts_by_user(
  user_id: UUID,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  if user_id != current_user.id and current_user.user_type != UserTypeEnum.ADMIN:
        raise HTTPException(status_code=403, detail="No permission")

  return crud.get_alerts_by_user(db, user_id)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
  alert_id: UUID,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  alert = crud.get_alert(db, alert_id)

  if not alert:
    raise HTTPException(status_code=404, detail="Alert not found")

  if alert.user_id != current_user.id and current_user.user_type != UserTypeEnum.ADMIN:
    raise HTTPException(status_code=403, detail="No permission")

  return alert


@router.post("/", response_model=AlertResponse)
def create_alert(data: AlertCreate, current_user: User = Depends(get_current_user),  db: Session = Depends(get_db)):
  if data.user_id != current_user.id and current_user.user_type != UserTypeEnum.ADMIN:
    raise HTTPException(status_code=403, detail="No permission")

  try:
    return crud.create_alert(db, data)
  except ValueError as e:
    raise HTTPException(status_code=409, detail=str(e))