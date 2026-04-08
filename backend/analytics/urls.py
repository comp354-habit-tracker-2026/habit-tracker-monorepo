from django.urls import path

from .views import AnalyticsOverviewView, HealthIndicatorsView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("health-indicators/", HealthIndicatorsView.as_view(), name="health_indicators"),
]
