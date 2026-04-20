from django.db.models import Avg, Sum, Max
from datetime import date
from activities.models import Activity


class AnalyticsRepository:
    def activity_statistics(self, user):
        queryset = Activity.objects.filter(account__user=user)
        return {
            "total_distance": queryset.aggregate(value=Sum("distance"))["value"] or 0,
            "total_calories": queryset.aggregate(value=Sum("calories"))["value"] or 0,
            "average_duration": queryset.aggregate(value=Avg("duration"))["value"] or 0,
            "activity_count": queryset.count(),
        }

    def trend_snapshot(self, user):
        return {
            "weekly_goal_completion": None,
            "notes": "Trend calculation contract in place; team can plug pandas/numpy implementation.",
        }

    def forecast_preview(self, user):
        return {
            "next_week_prediction": None,
            "model": "linear_regression_placeholder",
            "notes": "Forecast endpoint contract in place; team can plug scikit-learn model.",
        }

    def inactivity_evaluation(self, user):
        queryset = Activity.objects.filter(user=user)
        max_date = queryset.aggregate(max_date=Max('date'))['max_date']
        if max_date is None:
            days_since = None
            inactive = True
            severity = 'severe'
        else:
            days_since = (date.today() - max_date).days
            inactive = days_since >= 3
            if days_since < 3:
                severity = 'none'
            elif days_since < 7:
                severity = 'mild'
            else:
                severity = 'severe'
        return {
            'days_since_last_activity': days_since,
            'inactive': inactive,
            'severity': severity
        }

