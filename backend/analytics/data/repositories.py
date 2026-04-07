from datetime import timedelta

from django.db.models import Avg, Max, Sum
from datetime import date
from django.utils import timezone

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

    def activity_signal(self, user):
        today = timezone.localdate()
        recent_window_start = today - timedelta(days=7)

        queryset = Activity.objects.filter(user=user)
        recent_queryset = queryset.filter(date__gte=recent_window_start, date__lte=today)

        last_activity_date = queryset.order_by("-date").values_list("date", flat=True).first()

        weekly_sessions = recent_queryset.count()
        weekly_minutes = recent_queryset.aggregate(value=Sum("duration"))["value"] or 0

        return {
            "weekly_sessions": weekly_sessions,
            "weekly_minutes": int(weekly_minutes),
            "total_activity_count": queryset.count(),
            "days_since_last_activity": None
            if last_activity_date is None
            else (today - last_activity_date).days,
        }

    def activity_aggregates_for_window(self, user, start_date, end_date):
        queryset = Activity.objects.filter(user=user, date__gte=start_date, date__lte=end_date)

        total_minutes = int(queryset.aggregate(value=Sum("duration"))["value"] or 0)
        total_distance_km = float(queryset.aggregate(value=Sum("distance"))["value"] or 0)
        session_count = queryset.count()
        active_days = queryset.values("date").distinct().count()
        window_days = (end_date - start_date).days + 1

        last_activity_date = queryset.order_by("-date").values_list("date", flat=True).first()
        inactivity_streak_days = (
            window_days if last_activity_date is None else (end_date - last_activity_date).days
        )

        return {
            "total_minutes": total_minutes,
            "total_distance_km": round(total_distance_km, 2),
            "session_count": session_count,
            "active_days": active_days,
            "window_days": window_days,
            "inactivity_streak_days": inactivity_streak_days,
        }
