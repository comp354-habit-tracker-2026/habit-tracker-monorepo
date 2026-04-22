from django.urls import path

from presentation.views import DeleteNotificationView
from presentation.views import ViewNotifications
from presentation.views import MarkNotificationAsRead


urlpatterns = [
    path('notifications/<int:user_id>/', ViewNotifications.as_view()),
    path('notifications/<int:notification_id>/read/', MarkNotificationAsRead.as_view(), name="mark_notification_as_read"),
    path("<int:notification_id>/delete/", DeleteNotificationView.as_view(), name="delete-notification"),
]
