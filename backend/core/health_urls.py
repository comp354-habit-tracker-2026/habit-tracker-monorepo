from django.urls import path
from .health_views import HealthStatusView, HealthReadyView, HealthLiveView

urlpatterns = [
    path("health/", HealthStatusView.as_view(), name="health_status"),
    path("health/ready/", HealthReadyView.as_view(), name="health_ready"),
    path("health/live/", HealthLiveView.as_view(), name="health_live"),
]
