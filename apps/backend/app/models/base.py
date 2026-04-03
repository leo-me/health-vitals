# models/base.py
from app.db.base import Base        # ← 引入 Base

# 把所有 model 都 import 进来
from app.models.user import User
from app.models.health import HealthData
from app.models.alert import Alert
from app.models.device import Device
from app.models.sensor_recording import SensorRecording