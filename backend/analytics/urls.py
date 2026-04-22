from django.urls import path, include

from .views import AnalyticsOverviewView, HealthIndicatorsView, GoalProgressSeriesView, InactivitiesView, HealthTrackingView, HealthForecastView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
    path("goals/<int:goal_id>/progress-series/", GoalProgressSeriesView.as_view(), name="goal_progress_series"),
    path("inactivities-view", InactivitiesView.as_view(), name="inactivities_view"),
    path("health-tracking-view", HealthTrackingView.as_view(), name="health_tracking_view"),
    path("health-forecast-view", HealthForecastView.as_view(), name="health_forecast_view"),

]
