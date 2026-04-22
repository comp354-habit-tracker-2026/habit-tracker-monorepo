

"""Unit tests for NotificationService.

Uses mocks so no database is required.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from notifications.business.services import NotificationService


def make_goal(title="Run 5km", pk=1, current_value=100, target_value=100):
    goal = MagicMock()
    goal.pk = pk
    goal.title = title
    goal.current_value = current_value
    goal.target_value = target_value
    goal.user = MagicMock()
    return goal


class TestEvaluateGoalAchievement:
    def setup_method(self):
        self.service = NotificationService(repository=MagicMock())

    def test_achieved_when_current_equals_target(self):
        goal = make_goal(current_value=100, target_value=100)
        assert self.service.evaluate_goal_achievement(goal) is True

    def test_achieved_when_current_exceeds_target(self):
        goal = make_goal(current_value=120, target_value=100)
        assert self.service.evaluate_goal_achievement(goal) is True

    def test_not_achieved_when_below_target(self):
        goal = make_goal(current_value=50, target_value=100)
        assert self.service.evaluate_goal_achievement(goal) is False


class TestBuildAchievementMessage:
    def setup_method(self):
        self.service = NotificationService(repository=MagicMock())

    def test_message_contains_goal_title(self):
        goal = make_goal(title="Run 5km")
        message = self.service.build_achievement_message(goal)
        assert "Run 5km" in message


class TestBuildGoalProgressContent:
    def test_achieved_state(self):
        title, message = NotificationService._build_goal_progress_content("My Goal", "ACHIEVED")
        assert "achieved" in title.lower()
        assert "My Goal" in title
        assert "My Goal" in message

    def test_at_risk_state(self):
        title, message = NotificationService._build_goal_progress_content("My Goal", "AT_RISK")
        assert "at risk" in title.lower()
        assert "My Goal" in message

    def test_missed_state(self):
        title, message = NotificationService._build_goal_progress_content("My Goal", "MISSED")
        assert "missed" in title.lower()
        assert "My Goal" in message


class TestCreateGoalProgressNotification:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = NotificationService(repository=self.repo)
        self.computed_at = datetime(2026, 4, 1, tzinfo=timezone.utc)

    def _call(self, new_state, previous_state="ON_TRACK"):
        goal = make_goal()
        return self.service.create_goal_progress_notification(
            goal=goal,
            previous_state=previous_state,
            new_state=new_state,
            progress_summary={"percentComplete": 100.0},
            computed_at=self.computed_at,
        ), goal

    def test_achieved_creates_notification(self):
        result, goal = self._call("ACHIEVED")
        self.repo.create_notification.assert_called_once()
        assert result == self.repo.create_notification.return_value

    def test_at_risk_creates_notification(self):
        result, goal = self._call("AT_RISK")
        self.repo.create_notification.assert_called_once()

    def test_missed_creates_notification(self):
        result, goal = self._call("MISSED")
        self.repo.create_notification.assert_called_once()

    def test_on_track_returns_none(self):
        result, _ = self._call("ON_TRACK")
        assert result is None
        self.repo.create_notification.assert_not_called()

    def test_unknown_state_returns_none(self):
        result, _ = self._call("UNKNOWN")
        assert result is None

    def test_payload_contains_expected_fields(self):
        goal = make_goal(pk=42)
        self.service.create_goal_progress_notification(
            goal=goal,
            previous_state="ON_TRACK",
            new_state="ACHIEVED",
            progress_summary={"percentComplete": 100.0},
            computed_at=self.computed_at,
        )
        call_kwargs = self.repo.create_notification.call_args.kwargs
        payload = call_kwargs["payload"]
        assert payload["goalId"] == 42
        assert payload["newState"] == "ACHIEVED"
        assert payload["previousState"] == "ON_TRACK"


class TestListRecent:
    def test_delegates_to_repository(self):
        repo = MagicMock()
        service = NotificationService(repository=repo)
        user = MagicMock()
        result = service.list_recent(user)
        repo.list_recent.assert_called_once_with(user)
        assert result == repo.list_recent.return_value
