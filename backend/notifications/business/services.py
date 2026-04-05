from core.business import BaseService
from core.models import OutboxEvent
from notifications.data import NotificationRepository


class NotificationService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or NotificationRepository()

    def evaluate_goal_achievement(self, goal):
        return goal.current_value >= goal.target_value

    def build_achievement_message(self, goal):
        return f"Goal achieved: {goal.title}"

    def publish_goal_progress_state_changed(
        self,
        *,
        goal,
        previous_state,
        new_state,
        progress_summary,
        computed_at,
        dedup_key,
        event_id,
    ):
        """Write a GoalProgressStateChanged record to the outbox.

        This is a backend integration boundary for future notification delivery,
        not the step that sends email, push, or in-app messages directly.
        """

        payload = {
            "eventId": event_id,
            "userId": goal.user_id,
            "goalId": goal.pk,
            "previousState": previous_state,
            "newState": new_state,
            "computedAt": computed_at.isoformat(),
            "stateChangeAt": computed_at.isoformat(),
            "progressSummary": progress_summary,
            "dedupKey": dedup_key,
        }
        event, _ = OutboxEvent.objects.get_or_create(
            idempotency_key=dedup_key,
            defaults={"event_type": "GoalProgressStateChanged", "payload": payload},
        )
        return event

    def list_recent(self, user):
        return self.repository.list_recent(user)
