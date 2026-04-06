from django.urls import path
from .views import AnalyticsOverviewView, HealthIndicatorsView

from analytics.views import (
    AnalyticsOverviewView,
    ActivityStatisticsView,
    PersonalRecordsView,
    ActivityTypeBreakdownView,
    WeeklySummaryView,
    ActivityStreaksView,
    ActivityForecastView,
    PaginatedActivityHistoryView,
)

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("activity-statistics/", ActivityStatisticsView.as_view(), name="activity_statistics"),
    path("personal-records/", PersonalRecordsView.as_view(), name="personal_records"),
    path("activity-type-breakdown/", ActivityTypeBreakdownView.as_view(), name="activity_type_breakdown"),
    path("weekly-summary/", WeeklySummaryView.as_view(), name="weekly_summary"),
    path("activity-streaks/", ActivityStreaksView.as_view(), name="activity_streaks"),
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
    path("forecast/", ActivityForecastView.as_view(), name="activity_forecast"),
    path("activity-history/", PaginatedActivityHistoryView.as_view(), name="activity_history"),
]