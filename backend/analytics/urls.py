from django.urls import path

from analytics.views import (
    AnalyticsOverviewView,
    ActivityStatisticsView,
    PersonalRecordsView,
    ActivityTypeBreakdownView,
    WeeklySummaryView,
    ActivityStreaksView,
)

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("activity-statistics/", ActivityStatisticsView.as_view(), name="activity_statistics"),
    path("personal-records/", PersonalRecordsView.as_view(), name="personal_records"),
    path("activity-type-breakdown/", ActivityTypeBreakdownView.as_view(), name="activity_type_breakdown"),
    path("weekly-summary/", WeeklySummaryView.as_view(), name="weekly_summary"),
    path("activity-streaks/", ActivityStreaksView.as_view(), name="activity_streaks"),
]

