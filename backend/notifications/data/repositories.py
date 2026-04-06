from notifications.models import Notification, NotificationChannel, NotificationType, UserNotificationPreference
from core.data import BaseRepository
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)
    
    def create_notification(self, user: User, type: str, message: str, channel: str, scheduled_at=None):
        notification = Notification(
            user=user,
            type=type,
            message=message,
            channel=channel,
            scheduled_at=scheduled_at
        )
        notification.save()
        return notification
    
    def get_all(self, user_id: int):
        return Notification.objects.filter(user_id=user_id)
    
    def get(self, notification_id: int):
        return Notification.objects.get(id=notification_id)
    
    def delete(self, notification_id: int):
        Notification.objects.filter(id=notification_id).delete()
    
class UserPreferenceRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserNotificationPreference)

    def get_user_preferences(self, user: User):
        return UserNotificationPreference.objects.get(user=user)

    def update_user_prefernces(self, user_id, **update_user_prefernces):
        return True
