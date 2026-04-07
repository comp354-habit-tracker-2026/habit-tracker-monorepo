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
    
    def get_all(self, user: User):
        return Notification.objects.filter(user=user)
    
    def get(self, notification_id: int):
        return Notification.objects.get(id=notification_id)
    
    def delete(self, notification_id: int):
        Notification.objects.filter(id=notification_id).delete()
    
    def mark_as_read(self, notification_id: int):
        notification = self.get(notification_id)

        if notification.read:
            return notification
        
        notification.read = True
        notification.save()

        return notification
    
    def mark_all_as_read(self, user: User):
        Notification.objects.filter(user=user).update(read=True)
    
class UserPreferenceRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserNotificationPreference)

    def get_user_preferences(self, user: User):
        return UserNotificationPreference.objects.get(user=user)

    def update_user_prefernces(self, user_id, **update_user_prefernces):
        return True
