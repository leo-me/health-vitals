import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StressLevel(str, enum.Enum):
    LOW = 'low'
    MIDDLE = 'normal'
    MIDDLE_HIGH = 'middle_high'
    HIGH = "high"


class SweatingLevel(str, enum.Enum):
    LOW = 'low'
    MIDDLE = 'normal'
    HIGH = "high"


class SmartWatchOutput(BaseModel):
    timestamp: datetime
    stress_level: Optional[StressLevel] = None
    heart_rate: int
    acc: Optional[float] = None
    body_temperature: Optional[float] = None
    sweat_level: SweatingLevel


class WebDashboardOutput(BaseModel):
    timestamp: datetime
    stress_level: Optional[StressLevel] = None
    heart_rate: int
    body_temperature: Optional[float] = None
    sweat_level: SweatingLevel
    acc: Optional[float] = None


class MLOutput(BaseModel):
    timestamp: datetime
    bvp: Optional[float] = None
    acc: Optional[float] = None
    eda: Optional[float] = None
    heart_rate: int
    ibi: Optional[float] = None
    temperature: Optional[float] = None
    eda_scl: Optional[float] = None
    eda_scr: Optional[float] = None


Researcher_csv_columns = [
    'timestamp', 'bvp', 'eda', 'heart_rate', 'ibi',
    'temperature', 'eda_scl', 'eda_scr', 'acc_x', 'acc_y', 'acc_z'
]
