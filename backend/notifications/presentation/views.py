from notifications.business.services import NotificationService
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# --- YOUR FEATURE STARTS HERE ---
class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated] 

    def delete(self, request, notification_id):
        service = NotificationService()
        try:
       
            notification = service.get(notification_id)
            
            if not notification:
                return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND) 

            if notification.user.id != request.user.id:
                return Response({"error": "Unauthorized deletion attempt"}, status=status.HTTP_403_FORBIDDEN) 

        
            service.delete(notification_id)
            return Response(status=status.HTTP_204_NO_CONTENT) 
            
        except Exception:
            return Response({"error": "An internal error has occurred."}, status=status.HTTP_400_BAD_REQUEST) 
        
class NotificationsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = NotificationService()
        try:
            notifications = service.get_all_notifications(request.user.id)
            return Response({"notifications": notifications}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An internal error has occurred."}, status=status.HTTP_400_BAD_REQUEST)

class ViewNotifications(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        service = NotificationService()
        try:
            notifications = service.get_all_notifications(user_id)
            return Response({"notifications": notifications}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An internal error has occurred."}, status=status.HTTP_400_BAD_REQUEST)

class MarkNotificationAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        service = NotificationService()
        try:
            notification = service.get(notification_id)
            if not notification:
                return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
            if notification.user.id != request.user.id:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            service.mark_as_read(notification_id)
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An internal error has occurred."}, status=status.HTTP_400_BAD_REQUEST)
