from notifications.models import Notification, NotificationChannel, UserNotificationPreference, NotificationType
from core.business import BaseService
from notifications.data.repositories import NotificationRepository, UserPreferenceRepository
from django.contrib.auth import get_user_model
import threading

User = get_user_model()

User = get_user_model()

class NotificationService(BaseService):
    def __init__(self, repository=None, user_preferences_service=None):
        self.notification_repository = repository or NotificationRepository()
        self.user_preferences_service = user_preferences_service or UserPreferencesService()

    def notify(self, title: str, description: str, recipient_id: str, event_type: NotificationType):
        recipient = User.objects.get(id=recipient_id)
        if recipient is None:
            raise Exception(f"User: {recipient_id} does not exist")

        recipient_preferences = self.user_preferences_service.get_user_preferences(recipient)
        if (not recipient_preferences.email_enabled and not recipient_preferences.in_app_enabled):
            # if notifications disabled
            return
        
        def send_notification(type: NotificationType.choices):
            if (recipient_preferences.email_enabled):
                self.notification_repository.create_notification(recipient, type, description, NotificationChannel.EMAIL)
                # Send email notification
                return
            if (recipient_preferences.in_app_enabled):
                self.notification_repository.create_notification(recipient, type, description, NotificationChannel.IN_APP)
                # Send in app notification
                return

        if (event_type == NotificationType.ACHIEVEMENT and recipient_preferences.achievement_notifs):
            send_notification()
        if (event_type == NotificationType.INACTIVITY_REMINDER and recipient_preferences.inactivity_reminders):
            send_notification()
    
    def get_all_notifications(self, user_id): 
        user = User.objects.get(id=user_id)
        return self.notification_repository.get_all(user)

    def get(self, notification_id):
        return self.notification_repository.get(notification_id)
    
    def delete(self, notification_id):
        try:
            self.notification_repository.delete(notification_id)
        except Notification.DoesNotExist:
            raise Exception(f"Unable to delete notification {notification_id}, does not exist")
    
    def mark_as_read(self, notification_id):
        try:
            return self.notification_repository.mark_as_read(notification_id)
        except Notification.DoesNotExist:
            raise Exception(f"Unable to mark notification {notification_id} as read, does not exist")
    
    def mark_all_as_read(self, user_id):
        user = User.objects.get(id=user_id)
        self.notification_repository.mark_all_as_read(user)  

class UserPreferencesService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserPreferenceRepository()

    def update_user_preferences(self, user_id, **update_user_preferences):
        return
    
    def create_default_user_preferences(self, user_id):
        return
    
    def get_user_preferences(self, user: User) -> UserNotificationPreference:
        return self.repository.get_user_preferences(user)
