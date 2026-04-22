from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from notifications.business import NotificationService
from notifications.business.services import NotificationService

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
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 
        
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
