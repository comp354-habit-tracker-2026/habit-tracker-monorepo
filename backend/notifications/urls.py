from django.urls import path

from .views import NotificationsHealthView
from .views import ViewNotifications
from .views import MarkNotificationAsRead


urlpatterns = [
    path("health/", NotificationsHealthView.as_view(), name="notifications_health"),
    path('notifications/<int:user_id>/', ViewNotifications.as_view()),
    path('notifications/<int:notification_id>/read/', MarkNotificationAsRead.as_view(), name="mark_notification_as_read"),
]
