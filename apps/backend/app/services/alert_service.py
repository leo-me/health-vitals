# services/alert_service.py

from sqlalchemy.orm import Session
from app.models.sensor_recording import SensorRecording
from app.models.alert import Alert
from app.models.sensor_recording import SensorType
from app.crud import crud_alert
from app.schemas.alert import AlertCreate

# threshold
# heart_rate > 140 "Heart rate too high"
# heart_rate < 40  "Heart rate too low"
# accelerometer  > 2.0 "Abnormal movement detected"
# EDA -> complex


# def check_alert_rules(health_data):
#     if health_data.heart_rate > 120:
#         trigger_alert(user_id, "heart rate too high")


def check_and_trigger_alert(db: Session, recording: SensorRecording) -> Alert | None:
    value = recording.data.get('value')

    if recording.sensor_type == SensorType.HEART_RATE:

        if value is not None and  value > 140:
            return crud_alert.create_alert(db, AlertCreate(
                recording_id=recording.id,
                user_id=recording.user_id,
                content='heart rate too high'
            ));

        elif value is not None and  value  < 40:
            return crud_alert.create_alert(db, AlertCreate(
                recording_id=recording.id,
                user_id=recording.user_id,
                content='heart rate too low'
            ));

    if recording.sensor_type == SensorType.ACCELEROMETER:
        if  value is not None and  value > 2.0:
            return crud_alert.create_alert(db, AlertCreate(
                recording_id=recording.id,
                user_id=recording.user_id,
                content='move too quick'
            ));

    return None