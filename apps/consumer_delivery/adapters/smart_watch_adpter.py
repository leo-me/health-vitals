from base import IConsumerAdapter

class SmartWatchAdapter(IConsumerAdapter):
  name = 'smart_watch_adapter'

  def get_format(self):
    return super().get_format()


  def get_schema(self):
    return super().get_schema()


  def validate(self, data):
    return super().validate(data)


  def transform(self, data):
    return super().transform(data)


  def deliver(self, data):
    return super().deliver(data)


  def is_available(self, data):
    return super().is_available(data)

  def on_error(cls, subclass):
    return super().on_error(subclass)
