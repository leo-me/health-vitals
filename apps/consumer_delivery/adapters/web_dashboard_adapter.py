from base import IConsumerAdapter

from core.config import settings

from schemas.output import WebDashboardOutput


class WebDashboardAdapter(IConsumerAdapter):
  name= 'web_dashboard_adapter'


  def get_format(self):
    return settings.web_dashboard

  def get_schema(self):
    return WebDashboardOutput
