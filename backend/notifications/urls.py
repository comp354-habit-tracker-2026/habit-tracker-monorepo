from django.urls import path

from presentation.views import DeleteNotificationView, NotificationsListView, ViewNotifications, MarkNotificationAsRead 


urlpatterns = [
    path("", NotificationsListView.as_view(), name="notifications_list"),
    path('notifications/<int:user_id>/', ViewNotifications.as_view()),
    path('notifications/<int:notification_id>/read/', MarkNotificationAsRead.as_view(), name="mark_notification_as_read"),
    path("<int:notification_id>/delete/", DeleteNotificationView.as_view(), name="delete-notification"),
]
