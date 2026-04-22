from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.business import NotificationService


class NotificationsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = NotificationService()
        return Response(service.list_recent(request.user))


class NotificationsHealthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = NotificationService()
        return Response({"recent_notifications": service.list_recent(request.user)})
