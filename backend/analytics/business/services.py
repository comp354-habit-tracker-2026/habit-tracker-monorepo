from core.business import BaseService
from analytics.data import AnalyticsRepository


class AnalyticsService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or AnalyticsRepository()

    def activity_statistics(self, user):
        return self.repository.activity_statistics(user)

    def trend_snapshot(self, user):
        return self.repository.trend_snapshot(user)

    def forecast_preview(self, user):
        return self.repository.forecast_preview(user)
