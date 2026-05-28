from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.cheap import get_cheap


router = APIRouter()


@router.get("/{user_id}")
def cheap(user_id: UUID, db: Session = Depends(get_db)):
    """
    Minimum-work endpoint for the cache-overhead experiment:
    one indexed `LIMIT 1` query on `sensor_recordings`, no adapter transform,
    no Pydantic schema. Use as the true "cheap" baseline against
    `/data/smart_watch` (adapter chain) and `/overview` (hourly aggregate).
    """
    result = get_cheap(db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No HR data for user")
    return result
