import enum


class StressLevel(enum.Enum):
  LOW = 'low'
  MIDDLE = 'normal'
  MIDDLE_HIGH = 'middle_high'
  HIGH = "high"

class SweatingLevel(enum.Enum):
  LOW = 'low'
  MIDDLE = 'normal'
  HIGH = "high"


class SmartWatchOutput:
  timestamp: str
  stress_level: StressLevel
  heart_rate: int # heart beat per minute
  acc: float # Accelerometry
  body_temperature: float
  sweat_level: SweatingLevel




class WebDashboardOutput:
  timestamp: str
  stress_level: StressLevel
  heart_rate: int # heart beat per minute
  body_temperature: float
  sweat_level: SweatingLevel
  acc: float # Accelerometry




# class ResearcherOutput:
#   timestamp: str
#   bvp: float # blood volume pulse
#   acc: float # Accelerometry
#   eda: float # electrodermal activity
#   heart_rate: int
#   ibi: float # inner_beat_interval
#   temperature: float # body_temperature
#   eda_scl: float # skin conductance level μS (Electrodermal Activity)
#   eda_scr: float # skin conductance response μS

Researcher_csv_files = [
  'timestamp',
  'bvp',
  'eda',
  'heart_rate',
  'ibi',
  'temperature',
  'eda_scl',
  'eda_scr',
  'acc_x',
  'acc_y',
  'acc_z'
]


class MLOutput:
  timestamp: str
  bvp: float # blood volume pulse
  acc: float # Accelerometry
  eda: float # electrodermal activity
  heart_rate: int
  ibi: float # inner_beat_interval
  temperature: float # body_temperature
  eda_scl: float # skin conductance level μS (Electrodermal Activity)
  eda_scr: float # skin conductance response μS


