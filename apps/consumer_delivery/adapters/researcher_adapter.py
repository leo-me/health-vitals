from base import IConsumerAdapter

from core.config import settings

from schemas.output import Researcher_csv_files

class ResearcherAdapter(IConsumerAdapter):
  name = 'research_adapter'

  def get_format(self):
    return settings.model_config

  def get_schema(self):
    return  Researcher_csv_files