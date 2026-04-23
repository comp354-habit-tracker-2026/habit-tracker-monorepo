from notifications.models import Notification, NotificationChannel, NotificationType, UserNotificationPreference
from core.data import BaseRepository
from django.contrib.auth import get_user_model
from goals.models import Goal


User = get_user_model()

class NotificationRepository(BaseRepository):

    LIST_FIELDS = (
        "id",
        "notification_type",
        "title",
        "message",
        "is_read",
        "created_at",
        "goal_id",
        "payload",
    )

    def __init__(self):
        super().__init__(Notification)
    
    def create_notification(self, user, type: str, message: str, payload: str, channel: str, scheduled_at=None, goal: Goal=None): 
        notification = Notification(
            user=user,
            type=type,
            message=message,
            payload=payload,
            channel=channel,
            scheduled_at=scheduled_at,
            goal=goal
        )
        notification.save()
        return notification
    
    def get_all(self, user):
        return Notification.objects.filter(user=user)
    
    def get(self, notification_id: int):
        return Notification.objects.get(pk=notification_id)
    
    def delete(self, notification_id: int):
        Notification.objects.filter(pk=notification_id).delete()
    
    def mark_as_read(self, notification_id: int):
        notification = self.get(notification_id)

        if notification.read:
            return notification
        
        notification.read = True
        notification.save()

        return notification
    
    def mark_all_as_read(self, user):
        Notification.objects.filter(user=user).update(read=True)

    def list_recent(self, user):
        return list(
            Notification.objects.filter(user=user)
            .order_by("-created_at", "-id")
            .values(*self.LIST_FIELDS)
        )
    
class UserPreferenceRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserNotificationPreference)

    def get_user_preferences(self, user):
        preferences, _ = UserNotificationPreference.objects.get_or_create(user=user)
        return preferences

    def create_user_preferences(self, user):
        preferences, _ = UserNotificationPreference.objects.get_or_create(user=user)
        return preferences

    def update_user_preferences(self, user, **update_user_preferences):
        preferences = self.get_user_preferences(user)

        allowed_fields = {
            "email_enabled",
            "in_app_enabled",
            "achievement_notifs",
            "inactivity_reminders",
            "inactivity_threshold_days",
        }

        changed_fields = []
        for field, value in update_user_preferences.items():
            if field in allowed_fields:
                setattr(preferences, field, value)
                changed_fields.append(field)

        if changed_fields:
            preferences.save(update_fields=changed_fields)

        return preferences

    def update_user_prefernces(self, user_id, **update_user_prefernces):
        user = User.objects.get(id=user_id)
        return self.update_user_preferences(user, **update_user_prefernces)
