from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.business import NotificationService
from notifications.business.services import NotificationService

class NotificationsHealthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = NotificationService()
        return Response({"recent_notifications": service.list_recent(request.user)})

class ViewNotifications(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        service = NotificationService()
        notifications = service.get_all_notifications(user_id)

        data = list(notifications.values())

        return Response({"notifications": data})

class MarkNotificationAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):
        service = NotificationService()
        try:
            notification = service.mark_as_read(notification_id)
            return Response(
                {"detail": "Notification marked as read.", "id": notification.id}
            )
        except Exception as e:
            return Response({"error": str(e)}, status=404)
