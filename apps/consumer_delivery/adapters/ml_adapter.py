from base import IConsumerAdapter

from core.config import settings

from schemas.output import MLOutput


class MLAdapters(IConsumerAdapter):
  name = 'ml_adapter'


  def get_format(self):
    return settings.ml.output_format

  def get_schema(self):
    return MLOutput


  def validate(self, data):
    pass