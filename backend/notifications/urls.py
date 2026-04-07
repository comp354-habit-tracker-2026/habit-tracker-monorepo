from django.urls import path

from .views import NotificationsHealthView
from .views import ViewNotifications


urlpatterns = [
    path("health/", NotificationsHealthView.as_view(), name="notifications_health"),
    path('notifications/<int:user_id>/', ViewNotifications.as_view()),
]
