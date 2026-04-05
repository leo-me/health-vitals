from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.alert import AlertResponse, AlertCreate
from app.db.session import get_db
from app.crud import crud_alert  as crud



router = APIRouter(prefix="/alert", tags=["alerts"])


@router.get("/user/{user_id}", response_model=list[AlertResponse])
def get_alerts_by_user(user_id: str, db: Session = Depends(get_db)):
  return crud.get_alerts_by_user(db, user_id)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: UUID, db: Session = Depends(get_db)):
  alert = crud.get_alert(db, alert_id)
  if not alert:
    raise HTTPException(status_code=404, detail="Alert not found")
  return alert


  


@router.post("/", response_model=AlertResponse)
def create_alert(data: AlertCreate, db: Session = Depends(get_db)):
  try:
    return crud.create_alert(db, data)
  except ValueError as e:
    raise HTTPException(status_code=409, detail=str(e))