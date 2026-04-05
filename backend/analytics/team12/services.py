from core.business import BaseService

from analytics.team12.repositories import Team12AnalyticsRepository


class Team12AnalyticsService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or Team12AnalyticsRepository()

    def activity_statistics(self, user):
        return self.repository.activity_statistics(user)

    def personal_records(self, user):
        return self.repository.personal_records(user)

    def activity_type_breakdown(self, user):
        return self.repository.activity_type_breakdown(user)
