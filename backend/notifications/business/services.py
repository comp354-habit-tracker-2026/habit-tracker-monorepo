from core.business import BaseService
from notifications.data import NotificationRepository


class NotificationService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or NotificationRepository()

    def evaluate_goal_achievement(self, goal):
        return goal.current_value >= goal.target_value

    def build_achievement_message(self, goal):
        return f"Goal achieved: {goal.title}"

    def list_recent(self, user):
        return self.repository.list_recent(user)
