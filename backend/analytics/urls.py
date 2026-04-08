from django.urls import path
from .views import AnalyticsOverviewView, HealthIndicatorsView

from .views import AnalyticsOverviewView, HealthIndicatorsView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
]
from analytics.views import (
    AnalyticsOverviewView,
    ActivityStatisticsView,
    PersonalRecordsView,
    ActivityTypeBreakdownView,
    WeeklySummaryView,
    ActivityStreaksView,
    ActivityForecastView,
    PaginatedActivityHistoryView,
    HealthIndicatorsView,
    InactivitiesView,
    HealthForecastView,
    HealthTrackingView,
     
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
    path("inactivities/", InactivitiesView.as_view(), name="inactivities"),
    path("health-forecast/", HealthForecastView.as_view(), name="health_forecast"),
    path("health-tracking/", HealthTrackingView.as_view(), name="health_tracking"),
    path("forecast/", ActivityForecastView.as_view(), name="activity_forecast"),
    path("activity-history/", PaginatedActivityHistoryView.as_view(), name="activity_history"),
]

