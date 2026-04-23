from django.urls import path

from .presentation.views import DeleteNotificationView, MarkNotificationAsRead, NotificationsListView, ViewNotifications


urlpatterns = [
    path("", NotificationsListView.as_view(), name="notifications_list"),
    path('<int:user_id>/', ViewNotifications.as_view()),
    path('<int:notification_id>/read/', MarkNotificationAsRead.as_view(), name="mark_notification_as_read"),
    path("<int:notification_id>/delete/", DeleteNotificationView.as_view(), name="delete-notification"),
]
