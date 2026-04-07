from django.urls import path
from .views import health, MyWhooshSyncStatusView

urlpatterns = [
    path("health/", health, name="health"),
    path("mywhoosh/status", MyWhooshSyncStatusView.as_view(), name="mywhoosh-status"),
]
