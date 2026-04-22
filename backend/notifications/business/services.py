from notifications.models import Notification, NotificationChannel, UserNotificationPreference, NotificationType
from core.business import BaseService
from notifications.data.repositories import NotificationRepository, UserPreferenceRepository
from django.contrib.auth import get_user_model
import threading

User = get_user_model()


class NotificationService(BaseService):
    STATE_TO_NOTIFICATION_TYPE = {
        "ACHIEVED": Notification.NotificationType.GOAL_ACHIEVED,
        "AT_RISK": Notification.NotificationType.GOAL_AT_RISK,
        "MISSED": Notification.NotificationType.GOAL_MISSED,
    }

    def __init__(self, repository: NotificationRepository=None, user_preferences_service: UserPreferenceRepository=None):
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
    
    def list_recent(self, user_id):
        user = User.objects.get(id=user_id)
        return self.notification_repository.list_recent(user)
    
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

    def evaluate_goal_achievement(self, goal):
        return goal.current_value >= goal.target_value

    def build_achievement_message(self, goal):
        return f"Goal achieved: {goal.title}"

    def create_goal_progress_notification(
        self,
        *,
        goal,
        previous_state,
        new_state,
        progress_summary,
        computed_at,
    ):
        """Create an in-app notification when the health indicator changes."""

        notification_type = self.STATE_TO_NOTIFICATION_TYPE.get(new_state)
        if notification_type is None:
            return None

        title, message = self._build_goal_progress_content(goal.title, new_state)
        return self.repository.create_notification(
            user=goal.user,
            goal=goal,
            notification_type=notification_type,
            title=title,
            message=message,
            payload={
                "goalId": goal.pk,
                "goalTitle": goal.title,
                "previousState": previous_state,
                "newState": new_state,
                "computedAt": computed_at.isoformat(),
                "progressSummary": progress_summary,
            },
        )

    @staticmethod
    def _build_goal_progress_content(goal_title, new_state):
        if new_state == "ACHIEVED":
            return (f"Goal achieved: {goal_title}", f"You reached your goal \"{goal_title}\".")
        if new_state == "AT_RISK":
            return (f"Goal at risk: {goal_title}", f"Your goal \"{goal_title}\" is at risk and may need attention.")
        return (f"Goal missed: {goal_title}", f"Your goal \"{goal_title}\" ended before the target was reached.")

class UserPreferencesService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserPreferenceRepository()

    def update_user_preferences(self, user_id, **update_user_preferences):
        return
    
    def create_default_user_preferences(self, user_id):
        return
    
    def get_user_preferences(self, user: User) -> UserNotificationPreference:
        return self.repository.get_user_preferences(user)
