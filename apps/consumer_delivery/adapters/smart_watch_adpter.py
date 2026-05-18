from adapters.base import IConsumerAdapter
from core.config import settings
from schemas.output import SmartWatchOutput, SweatingLevel, StressLevel


class SmartWatchAdapter(IConsumerAdapter):
    name = 'smart_watch_adapter'

    def get_format(self):
        return settings.smart_watch.output_format

    def get_schema(self):
        return SmartWatchOutput

    def validate(self, data):
        pass

    def transform(self, data) -> SmartWatchOutput:
        return SmartWatchOutput(
            timestamp=data.timestamp,
            heart_rate=int(data.hr),
            sweat_level=self._eda_to_sweat_level(data.eda or 0.0),
            stress_level=self._compute_stress(data.hr, data.eda or 0.0),
            acc=data.acc,
            body_temperature=data.temperature,
        )

    def deliver(self, data):
        pass

    def is_available(self, data):
        return True

    def on_error(cls, subclass):
        pass
