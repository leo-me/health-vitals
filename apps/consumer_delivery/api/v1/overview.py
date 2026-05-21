from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.session import get_db
from services.overview import get_overview


router = APIRouter()


@router.get("/{user_id}")
def overview(
    user_id: UUID,
    days: int = Query(7, ge=1, le=365, description="Window size in days"),
    db: Session = Depends(get_db),
):
    """
    Hourly-bucketed aggregation of one user's sensor readings over the past
    `days` days (anchored at their most-recent timestamp). Designed as the
    "expensive query" arm of the cache-latency experiment — touches up to
    millions of rows and is therefore the workload where Redis caching is
    expected to actually win.
    """
    result = get_overview(db, user_id, days)
    if result is None:
        raise HTTPException(status_code=404, detail="No sensor data for user")
    return result
