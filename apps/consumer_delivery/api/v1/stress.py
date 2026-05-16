from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.delivery import get_consumer_data

router = APIRouter()


@router.get("/{consumer_type}/{user_id}")
def get_data(consumer_type: str, user_id: UUID, db: Session = Depends(get_db)):
    result = get_consumer_data(db, consumer_type, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No sensor data found for this user")
    return result
