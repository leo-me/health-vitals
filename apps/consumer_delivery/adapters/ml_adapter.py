from adapters.base import IConsumerAdapter
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

    def transform(self, data) -> MLOutput:
        return MLOutput(
            timestamp=data.timestamp,
            heart_rate=int(data.hr),
            bvp=data.bvp,
            acc=data.acc,
            eda=data.eda,
            ibi=data.ibi,
            temperature=data.temperature,
            eda_scl=data.eda_scl,
            eda_scr=data.eda_scr,
        )

    def deliver(self, data):
        pass

    def is_available(self, data):
        return True

    def on_error(cls, subclass):
        pass
