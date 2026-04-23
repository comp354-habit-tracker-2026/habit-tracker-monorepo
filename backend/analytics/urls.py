from django.urls import path, include

from .views import AnalyticsOverviewView, HealthIndicatorsView, GoalProgressSeriesView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
    path("goals/<int:goal_id>/progress-series/", GoalProgressSeriesView.as_view(), name="goal_progress_series"),
]
