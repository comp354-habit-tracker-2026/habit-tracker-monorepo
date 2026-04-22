from django.urls import path

from .views import AnalyticsOverviewView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
]

