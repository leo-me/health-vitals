from app.models.sensor_recording import SensorRecording, SensorType
from app.services.alert_service import check_and_trigger_alert
from app.models.alert import Alert

from unittest.mock import MagicMock, patch




def test_trigger_high_heart_rate_alert(db, recording_ids):
  # alert_before = db.query(Alert).all()

  # recording = SensorRecording(
  #   id=recording_ids["id"],
  #   device_id=recording_ids["device_id"],
  #   user_id=recording_ids["user_id"],
  #   sensor_type=SensorType.HEART_RATE,
  #   data={
  #     "value": 150,
  #   }
  # )

  # check_and_trigger_alert(db, recording)

  # alert_after = db.query(Alert).all()

  # assert len(alert_after) == len(alert_before) + 1
  db = MagicMock()
  recording = SensorRecording(
    id=recording_ids["id"],
    device_id=recording_ids["device_id"],
    user_id=recording_ids["user_id"],
    sensor_type=SensorType.HEART_RATE,
    data={
      "value": 150,
    }
  )
  with patch("app.services.alert_service.crud_alert.create_alert") as mock_create:
    mock_create.return_value = MagicMock()
    check_and_trigger_alert(db, recording)

    mock_create.assert_called_once()
  


def test_trigger_low_heart_rate_alert(db, recording_ids):
  # alert_before = db.query(Alert).all()

  # recording = SensorRecording(
  #   id=recording_ids["id"],
  #   device_id=recording_ids["device_id"],
  #   user_id=recording_ids["user_id"],
  #   sensor_type=SensorType.HEART_RATE,
  #   data={
  #     "value": 40,
  #   }
  # )

  # check_and_trigger_alert(db, recording)

  # alert_after = db.query(Alert).all()

  # assert len(alert_after) == len(alert_before) + 1

  db = MagicMock()
  recording = SensorRecording(
    id=recording_ids["id"],
    device_id=recording_ids["device_id"],
    user_id=recording_ids["user_id"],
    sensor_type=SensorType.HEART_RATE,
    data={
      "value": 39,
    }
  )
  with patch("app.services.alert_service.crud_alert.create_alert") as mock_create:
    mock_create.return_value = MagicMock()
    check_and_trigger_alert(db, recording)

    mock_create.assert_called_once()

def test_not_trigger_heart_rate_alert(db, recording_ids):
  db = MagicMock()
  recording = SensorRecording(
    id=recording_ids["id"],
    device_id=recording_ids["device_id"],
    user_id=recording_ids["user_id"],
    sensor_type=SensorType.HEART_RATE,
    data={
      "value": 40,
    }
  )
  with patch("app.services.alert_service.crud_alert.create_alert") as mock_create:
    mock_create.return_value = MagicMock()
    check_and_trigger_alert(db, recording)

    mock_create.assert_not_called()


def test_trigger_high_accelerometer_alert(db, recording_ids):
  # alert_before = db.query(Alert).all()

  # recording = SensorRecording(
  #   id=recording_ids["id"],
  #   device_id=recording_ids["device_id"],
  #   user_id=recording_ids["user_id"],
  #   sensor_type=SensorType.ACCELEROMETER,
  #   data={
  #     "value": 3.2,
  #   }
  # )

  # check_and_trigger_alert(db, recording)

  # alert_after = db.query(Alert).all()

  # assert len(alert_after) == len(alert_before) + 1


  db = MagicMock()
  recording = SensorRecording(
    id=recording_ids["id"],
    device_id=recording_ids["device_id"],
    user_id=recording_ids["user_id"],
    sensor_type=SensorType.ACCELEROMETER,
    data={
      "value": 3.2,
    }
  )

  with patch("app.services.alert_service.crud_alert.create_alert") as mock_create:
    mock_create.return_value = MagicMock()
    check_and_trigger_alert(db, recording)

    mock_create.assert_called_once()