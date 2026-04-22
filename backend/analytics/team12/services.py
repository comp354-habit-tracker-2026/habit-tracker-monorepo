
from analytics.team12.repositories import Team12AnalyticsRepository


class Team12AnalyticsService:
    def __init__(self, repository=None):
        self.repository = repository or Team12AnalyticsRepository()

    def activity_statistics(self, user):
        return self.repository.activity_statistics(user)

    def personal_records(self, user):
        return self.repository.personal_records(user)

    def activity_type_breakdown(self, user):
        return self.repository.activity_type_breakdown(user)

    def weekly_summary(self, user, from_param, to_param, activity_type=None):
        return self.repository.weekly_summary(
            user=user,
            from_param=from_param,
            to_param=to_param,
            activity_type=activity_type,
        )

    def activity_streaks(self, user):
        return self.repository.activity_streaks(user)

    # Generated with help from an LLM.
    def monthly_summary(self, user, from_param, to_param, activity_type=None):
        return self.repository.monthly_summary(
            user=user,
            from_param=from_param,
            to_param=to_param,
            activity_type=activity_type,
        )
    
    def personal_record_for_habit(self, user, activity_type, metric_type):
        return self.repository.personal_record_for_habit(user, activity_type, metric_type)
