from uuid import UUID

from sqlalchemy.orm import Session
from app.schemas.alert import AlertCreate
from app.models.alert import Alert




def create_alert(db: Session, data: AlertCreate) -> Alert:
  alert = Alert(**data.model_dump(exclude_none=True))
  db.add(alert)
  db.commit();
  db.refresh(alert)

  return alert


def get_alert(db: Session, alert_id: UUID):
  alert = db.query(Alert).filter(Alert.id == alert_id).first()

  if not alert:
    raise ValueError('Alert not found')
  return alert

def get_alerts_by_user(db: Session, user_id: UUID) -> list[Alert]:
  return db.query(Alert).filter(Alert.user_id == user_id).all()