from django.urls import path
from .views import NotificationsHealthView, DeleteNotificationView

urlpatterns = [
    path("health/", NotificationsHealthView.as_view(), name="notifications_health"),

    path("<int:notification_id>/delete/", DeleteNotificationView.as_view(), name="delete-notification"),
]