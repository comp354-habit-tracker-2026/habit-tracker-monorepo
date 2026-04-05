from datetime import date, datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from analytics.business import GoalProgressService
from core.models import OutboxEvent
from goals.models import Goal

User = get_user_model()


def _dt(year, month, day):
    return timezone.make_aware(datetime(year, month, day, 12, 0, 0))


@pytest.mark.django_db
class TestGoalProgressService:
    def setup_method(self):
        self.user = User.objects.create_user(
            username="goal-progress-user",
            email="goal-progress@example.com",
            password="TestPass123!",
        )
        self.service = GoalProgressService()

    def test_state_change_to_achieved_publishes_one_event(self):
        goal = Goal.objects.create(
            user=self.user,
            title="Run 100km",
            target_value=100,
            current_value=100,
            goal_type="distance",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 30),
        )

        result = self.service.evaluate_goal(goal, computed_at=_dt(2026, 4, 10))

        goal.refresh_from_db()
        event = OutboxEvent.objects.get()
        assert result["state"] == Goal.ProgressState.ACHIEVED
        assert result["event_published"] is True
        assert goal.progress_state == Goal.ProgressState.ACHIEVED
        assert event.event_type == "GoalProgressStateChanged"
        assert event.payload["previousState"] == Goal.ProgressState.ON_TRACK
        assert event.payload["newState"] == Goal.ProgressState.ACHIEVED
        assert event.payload["progressSummary"]["percentComplete"] == 100.0

    def test_state_change_to_at_risk_only_publishes_once(self):
        goal = Goal.objects.create(
            user=self.user,
            title="Workout streak",
            target_value=100,
            current_value=10,
            goal_type="custom",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 11),
        )

        first = self.service.evaluate_goal(goal, computed_at=_dt(2026, 4, 10))
        second = self.service.evaluate_goal(goal, computed_at=_dt(2026, 4, 10))

        goal.refresh_from_db()
        assert first["state"] == Goal.ProgressState.AT_RISK
        assert second["event_published"] is False
        assert goal.progress_state == Goal.ProgressState.AT_RISK
        assert OutboxEvent.objects.count() == 1

    def test_state_change_to_missed_publishes_after_deadline(self):
        goal = Goal.objects.create(
            user=self.user,
            title="Daily calories",
            target_value=400,
            current_value=150,
            goal_type="calories",
            progress_state=Goal.ProgressState.AT_RISK,
            progress_state_changed_at=timezone.now(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 10),
        )

        result = self.service.evaluate_goal(goal, computed_at=_dt(2026, 4, 12))

        event = OutboxEvent.objects.get()
        assert result["state"] == Goal.ProgressState.MISSED
        assert event.payload["previousState"] == Goal.ProgressState.AT_RISK
        assert event.payload["newState"] == Goal.ProgressState.MISSED

    def test_on_track_transition_updates_goal_without_publishing(self):
        goal = Goal.objects.create(
            user=self.user,
            title="Build consistency",
            target_value=100,
            current_value=50,
            goal_type="custom",
            progress_state=Goal.ProgressState.AT_RISK,
            progress_state_changed_at=timezone.now(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 30),
        )

        result = self.service.evaluate_goal(goal, computed_at=_dt(2026, 4, 5))

        goal.refresh_from_db()
        assert result["state"] == Goal.ProgressState.ON_TRACK
        assert result["event_published"] is False
        assert goal.progress_state == Goal.ProgressState.ON_TRACK
        assert goal.progress_state_changed_at is not None
        assert OutboxEvent.objects.count() == 0
