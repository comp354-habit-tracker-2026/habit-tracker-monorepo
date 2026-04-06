from core.business import BaseService
from notifications.data import NotificationRepository
from notifications.models import Notification


class NotificationService(BaseService):
    STATE_TO_NOTIFICATION_TYPE = {
        "ACHIEVED": Notification.NotificationType.GOAL_ACHIEVED,
        "AT_RISK": Notification.NotificationType.GOAL_AT_RISK,
        "MISSED": Notification.NotificationType.GOAL_MISSED,
    }

    def __init__(self, repository=None):
        self.repository = repository or NotificationRepository()

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

    def list_recent(self, user):
        return self.repository.list_recent(user)
