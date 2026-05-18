from adapters.base import IConsumerAdapter
from core.config import settings
from schemas.output import ResearcherOutput, Researcher_csv_columns


class ResearcherAdapter(IConsumerAdapter):
    name = 'researcher_adapter'

    def get_format(self):
        return settings.researcher.output_format

    def get_schema(self):
        return Researcher_csv_columns

    def validate(self, data):
        pass

    def transform(self, data) -> ResearcherOutput:
        return ResearcherOutput(
            timestamp=data.timestamp,
            heart_rate=int(data.hr),
            bvp=data.bvp,
            eda=data.eda,
            ibi=data.ibi,
            temperature=data.temperature,
            eda_scl=data.eda_scl,
            eda_scr=data.eda_scr,
            acc_x=data.acc_x,
            acc_y=data.acc_y,
            acc_z=data.acc_z,
        )

    def deliver(self, data):
        pass

    def is_available(self, data):
        return True

    def on_error(cls, subclass):
        pass
