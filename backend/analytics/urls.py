from django.urls import path, include

from analytics.views import (
    AnalyticsOverviewView, HealthIndicatorsView, InactivitiesView, HealthTrackingView, HealthForecastView, GoalProgressSeriesView,
    ActivityStatisticsView,
    PersonalRecordsView,
    ActivityTypeBreakdownView,
    WeeklySummaryView,
    ActivityStreaksView,
    ActivityForecastView,
    PaginatedActivityHistoryView,  GoalInsightsView, GoalCompletionRateView,AtRiskGoalsView, GoalsAnalyticsSummaryView
)

from .views import AnalyticsOverviewView
from .views import personal_record_view

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
    path("goals/<int:goal_id>/progress-series/", GoalProgressSeriesView.as_view(), name="goal_progress_series"),
    path("inactivities-view", InactivitiesView.as_view(), name="inactivities_view"),
    path("health-tracking-view", HealthTrackingView.as_view(), name="health_tracking_view"),
    path("health-forecast-view", HealthForecastView.as_view(), name="health_forecast_view"),
    path("activity-statistics/", ActivityStatisticsView.as_view(), name="activity_statistics"),
    path("personal-records/", PersonalRecordsView.as_view(), name="personal_records"),
    path("activity-type-breakdown/", ActivityTypeBreakdownView.as_view(), name="activity_type_breakdown"),
    path("weekly-summary/", WeeklySummaryView.as_view(), name="weekly_summary"),
    path("activity-streaks/", ActivityStreaksView.as_view(), name="activity_streaks"),
    path("forecast/", ActivityForecastView.as_view(), name="activity_forecast"),
    path("activity-history/", PaginatedActivityHistoryView.as_view(), name="activity_history"),
    path("goal-insights-view/", GoalInsightsView.as_view(), name="goal_insights_view"),
    path("goal-completion-rate-view/", GoalCompletionRateView.as_view(), name="goal_completion_rate_view"),
    path("at-risk-goals-view/", AtRiskGoalsView.as_view(), name="at_risk_goals_view"),
    path("goals-analytics-summary-view/", GoalsAnalyticsSummaryView.as_view(), name="goals_analytics_summary_view"),

]

urlpatterns = [
    path("personal-record/<int:habit_id>/", personal_record_view),
]
