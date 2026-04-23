from django.urls import path
from .views import health, MyWhooshSyncStatusView, MyWhooshSyncView

urlpatterns = [
    path("health/", health, name="health"),
    path("mywhoosh/sync", MyWhooshSyncView.as_view(), name="mywhoosh-sync"),
    path("mywhoosh/status", MyWhooshSyncStatusView.as_view(), name="mywhoosh-status"),
]
