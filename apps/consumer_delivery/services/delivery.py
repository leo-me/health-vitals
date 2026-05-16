from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from adapters.smart_watch_adpter import SmartWatchAdapter
from core.cache import cache_get, cache_set
from core.config import settings
from models.sensor_recording import SensorRecording, SensorType


@dataclass
class SensorData:
    timestamp: datetime
    hr: float = 0.0
    eda: float = 0.0
    acc: float = 0.0
    temperature: float = 0.0
    ibi: float = 0.0
    bvp: float = 0.0
    eda_scl: float = 0.0
    eda_scr: float = 0.0


# (adapter_instance, cache_ttl_seconds)
_ADAPTERS = {
    "smart_watch": (SmartWatchAdapter(), int(settings.smart_watch.data_frequency // 1000)),
}


def _latest(db: Session, user_id: UUID, sensor_type: SensorType) -> Optional[SensorRecording]:
    return (
        db.query(SensorRecording)
        .filter(
            SensorRecording.user_id == user_id,
            SensorRecording.sensor_type == sensor_type,
        )
        .order_by(SensorRecording.timestamp.desc())
        .first()
    )


def _build_sensor_data(db: Session, user_id: UUID) -> Optional[SensorData]:
    hr_rec = _latest(db, user_id, SensorType.HEART_RATE)
    if hr_rec is None:
        return None
    eda_rec = _latest(db, user_id, SensorType.EDA)
    return SensorData(
        timestamp=hr_rec.timestamp,
        hr=hr_rec.data.get("value", 0.0),
        eda=eda_rec.data.get("value", 0.0) if eda_rec else 0.0,
    )


def get_consumer_data(db: Session, consumer_type: str, user_id: UUID) -> Optional[dict]:
    cache_key = f"{consumer_type}:{user_id}"

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

    cache_set(cache_key, result, ttl_seconds=max(ttl, 1))
    return result
