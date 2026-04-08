from django.urls import path, include

from .views import AnalyticsOverviewView, HealthIndicatorsView

from analytics.progess_series.views import GoalProgressSeriesView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
]
