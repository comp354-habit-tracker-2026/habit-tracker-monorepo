from django.db.models import Avg, Sum

from activities.models import Activity


class AnalyticsRepository:
    def activity_statistics(self, user):
        queryset = Activity.objects.filter(user=user)
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
