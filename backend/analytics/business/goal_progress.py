from decimal import Decimal
from uuid import uuid4

from django.utils import timezone

from goals.models import Goal
from notifications.business import NotificationService


class GoalProgressService:
    """Compute goal progress state from stored goal data and record state changes.

    This service updates the goal's last computed state and only asks the
    notification layer to record an event contract when a notifiable state is
    reached.
    """

    AT_RISK_TOLERANCE = Decimal("0.10")
    NOTIFIABLE_STATES = {
        Goal.ProgressState.ACHIEVED,
        Goal.ProgressState.AT_RISK,
        Goal.ProgressState.MISSED,
    }

    def __init__(self, notification_service=None):
        self.notification_service = notification_service or NotificationService()

    def evaluate_goal(self, goal, computed_at=None):
        computed_at = self._normalize_timestamp(computed_at or timezone.now())
        previous_state = goal.progress_state
        new_state, progress_summary = self._compute_state(goal, computed_at)
        event_published = False

        if previous_state != new_state:
            # Persist the latest computed state so later checks can detect transitions.
            goal.progress_state = new_state
            goal.progress_state_changed_at = computed_at
            goal.save(update_fields=["progress_state", "progress_state_changed_at", "updated_at"])

            if new_state in self.NOTIFIABLE_STATES:
                # Record the outbox/event contract for future notification delivery.
                self.notification_service.publish_goal_progress_state_changed(
                    goal=goal,
                    previous_state=previous_state,
                    new_state=new_state,
                    progress_summary=progress_summary,
                    computed_at=computed_at,
                    dedup_key=f"goal-progress:{goal.pk}:{new_state}:{computed_at.isoformat()}",
                    event_id=str(uuid4()),
                )
                event_published = True

        return {
            "goal_id": goal.pk,
            "previous_state": previous_state,
            "state": new_state,
            "changed": previous_state != new_state,
            "event_published": event_published,
            "progress_summary": progress_summary,
        }

    def _compute_state(self, goal, computed_at):
        today = timezone.localdate(computed_at)
        actual = Decimal(goal.current_value)
        target = Decimal(goal.target_value) if goal.target_value else Decimal("0")
        percent_complete = Decimal("0")
        completion_ratio = Decimal("0")

        if target > 0:
            completion_ratio = min(Decimal("1"), actual / target)
            percent_complete = min(Decimal("100"), completion_ratio * 100)

        if target > 0 and actual >= target:
            state = Goal.ProgressState.ACHIEVED
        elif today > goal.end_date:
            state = Goal.ProgressState.MISSED
        else:
            total_days = max((goal.end_date - goal.start_date).days, 1)
            elapsed_days = min(max((today - goal.start_date).days, 0), total_days)
            expected_ratio = Decimal(elapsed_days) / Decimal(total_days)
            if completion_ratio + self.AT_RISK_TOLERANCE < expected_ratio:
                state = Goal.ProgressState.AT_RISK
            else:
                state = Goal.ProgressState.ON_TRACK

        progress_summary = {
            "actual": float(actual),
            "target": float(target),
            "percentComplete": float(percent_complete),
            "timeRemainingSec": max((goal.end_date - today).days, 0) * 86400,
            "periodStart": goal.start_date.isoformat(),
            "periodEnd": goal.end_date.isoformat(),
        }
        return state, progress_summary

    @staticmethod
    def _normalize_timestamp(value):
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value
