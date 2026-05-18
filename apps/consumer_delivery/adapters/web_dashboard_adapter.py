from adapters.base import IConsumerAdapter
from core.config import settings
from schemas.output import WebDashboardOutput, SweatingLevel, StressLevel


class WebDashboardAdapter(IConsumerAdapter):
    name = 'web_dashboard_adapter'

    def get_format(self):
        return settings.web_dashboard.output_format

    def get_schema(self):
        return WebDashboardOutput

    def validate(self, data):
        pass

    def transform(self, data) -> WebDashboardOutput:
        return WebDashboardOutput(
            timestamp=data.timestamp,
            heart_rate=int(data.hr),
            sweat_level=self._eda_to_sweat_level(data.eda or 0.0),
            stress_level=self._compute_stress(data.hr, data.eda or 0.0),
            body_temperature=data.temperature,
            acc=data.acc,
        )

    def deliver(self, data):
        pass

    def is_available(self, data):
        return True

    def on_error(cls, subclass):
        pass
