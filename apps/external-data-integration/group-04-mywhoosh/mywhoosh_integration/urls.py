from django.urls import path
from .views import health

urlpatterns = [
    path("health/", health, name="health"),
]

#which one to keep?
from mywhoosh_integration.views import MyWhooshSyncStatusView

urlpatterns = [
    path("mywhoosh/status", MyWhooshSyncStatusView.as_view(), name="mywhoosh-status"),
]
