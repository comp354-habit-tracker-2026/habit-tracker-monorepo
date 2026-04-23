from django.urls import path

from notifications.presentation.views import NotificationsHealthView, NotificationsListView

urlpatterns = [
    path("", NotificationsListView.as_view(), name="notifications_list"),
    path("health/", NotificationsHealthView.as_view(), name="notifications_health"),
]
