from django.urls import path

from .views import NotificationsHealthView

urlpatterns = [
    path("health/", NotificationsHealthView.as_view(), name="notifications_health"),
]
