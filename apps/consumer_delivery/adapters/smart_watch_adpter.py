from adapters.base import IConsumerAdapter

from core.config import settings

from schemas.output import SmartWatchOutput, SweatingLevel

class SmartWatchAdapter(IConsumerAdapter):
  name = 'smart_watch_adapter'

  def get_format(self):
    return settings.smart_watch.output_format


  def get_schema(self):
    return SmartWatchOutput


  def validate(self, data):
    return super().validate(data)


  def transform(self, data) -> SmartWatchOutput:
    # get data from database


    # transform to output schema
    return SmartWatchOutput(
      heart_rate=data.hr,
      sweat_level=self._eda_to_sweat_level(data.eda),
      timestamp=data.timestamp
    )


  def deliver(self, data):
    return super().deliver(data)


  def is_available(self, data):
    return super().is_available(data)

  def on_error(cls, subclass):
    return super().on_error(subclass)



  def _eda_to_sweat_level(self, eda: float) -> SweatingLevel:
    if eda < 1.0:
        return SweatingLevel.LOW
    elif eda < 5.0:
        return SweatingLevel.MEDIUM
    else:
        return SweatingLevel.HIGH