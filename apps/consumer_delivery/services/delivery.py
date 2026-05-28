import math
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from adapters.smart_watch_adpter import SmartWatchAdapter
from adapters.web_dashboard_adapter import WebDashboardAdapter
from adapters.ml_adapter import MLAdapters
from adapters.researcher_adapter import ResearcherAdapter
from core.cache import cache_get, cache_set
from core.config import settings
from models.sensor_recording import SensorRecording, SensorType

_CACHE_ENABLED = (os.getenv("CACHE_ENABLED", "true").lower() != "false")


@dataclass
class SensorData:
    timestamp: datetime
    hr: float = 0.0
    eda: Optional[float] = None
    bvp: Optional[float] = None
    acc_x: Optional[float] = None
    acc_y: Optional[float] = None
    acc_z: Optional[float] = None
    temperature: Optional[float] = None
    ibi: Optional[float] = None
    eda_scl: Optional[float] = None
    eda_scr: Optional[float] = None

    @property
    def acc(self) -> Optional[float]:
        if self.acc_x is None:
            return None
        return round(math.sqrt(self.acc_x**2 + self.acc_y**2 + self.acc_z**2), 4)


_ADAPTERS = {
    "smart_watch":   (SmartWatchAdapter(),   settings.smart_watch.data_frequency // 1000),
    "web_dashboard": (WebDashboardAdapter(), settings.web_dashboard.data_frequency // 1000),
    "ml":            (MLAdapters(),          settings.ml.data_frequency // 1000),
    "researcher":    (ResearcherAdapter(),   settings.researcher.data_frequency // 1000),
}


_SENSOR_TYPES = (
    SensorType.HEART_RATE,
    SensorType.EDA,
    SensorType.BVP,
    SensorType.ACC,
    SensorType.IBI,
    SensorType.TEMP,
)


def _latest_per_sensor(db: Session, user_id: UUID) -> dict[SensorType, SensorRecording]:
    # Single round-trip: DISTINCT ON (sensor_type) ordered by timestamp DESC
    # returns the most recent row for each sensor type in one query.
    rows = (
        db.query(SensorRecording)
        .filter(
            SensorRecording.user_id == user_id,
            SensorRecording.sensor_type.in_(_SENSOR_TYPES),
        )
        .distinct(SensorRecording.sensor_type)
        .order_by(SensorRecording.sensor_type, SensorRecording.timestamp.desc())
        .all()
    )
    return {r.sensor_type: r for r in rows}


def _build_sensor_data(db: Session, user_id: UUID) -> Optional[SensorData]:
    by_type = _latest_per_sensor(db, user_id)

    hr_rec = by_type.get(SensorType.HEART_RATE)
    if hr_rec is None:
        return None

    eda_rec  = by_type.get(SensorType.EDA)
    bvp_rec  = by_type.get(SensorType.BVP)
    acc_rec  = by_type.get(SensorType.ACC)
    ibi_rec  = by_type.get(SensorType.IBI)
    temp_rec = by_type.get(SensorType.TEMP)

    acc_data = acc_rec.data if acc_rec else None

    return SensorData(
        timestamp=hr_rec.timestamp,
        hr=hr_rec.data.get("value", 0.0),
        eda=eda_rec.data.get("value") if eda_rec else None,
        bvp=bvp_rec.data.get("value") if bvp_rec else None,
        acc_x=acc_data.get("x") if acc_data else None,
        acc_y=acc_data.get("y") if acc_data else None,
        acc_z=acc_data.get("z") if acc_data else None,
        ibi=ibi_rec.data.get("ibi_s") if ibi_rec else None,
        temperature=temp_rec.data.get("value") if temp_rec else None,
    )


def get_consumer_data(db: Session, consumer_type: str, user_id: UUID) -> Optional[dict]:
    cache_key = f"{consumer_type}:{user_id}"

    if _CACHE_ENABLED:
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

    if consumer_type not in _ADAPTERS:
        return None

    sensor_data = _build_sensor_data(db, user_id)
    if sensor_data is None:
        return None

    adapter, ttl = _ADAPTERS[consumer_type]
    output = adapter.transform(sensor_data)
    result = output.model_dump()

    if _CACHE_ENABLED:
        cache_set(cache_key, result, ttl_seconds=max(ttl, 1))
    return result
