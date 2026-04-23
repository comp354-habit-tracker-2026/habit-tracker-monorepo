# Written by Gorav-K; Claude (Anthropic AI) assisted with fixing tests to pass on GitHub CI.
# Source: Claude Sonnet 4.6 via Claude Code CLI (Anthropic, 2026).
# Required disclosure per COMP 354 AI-generated code traceability policy.
#
# Gorav-K — GitHub: Gorav-K
# Issue #196: Unit tests for NotificationService
# Branch: feature/group-15-health-indicators


"""Unit tests for NotificationService.

Uses mocks so no database is required.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from notifications.business.services import NotificationService, UserPreferencesService
from notifications.models import NotificationType


def make_goal(title="Run 5km", pk=1, current_value=100, target_value=100):
    goal = MagicMock()
    goal.pk = pk
    goal.title = title
    goal.current_value = current_value
    goal.target_value = target_value
    goal.user = MagicMock()
    goal.user.id = 1
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
        self.recipient = MagicMock()
        self.preferences = MagicMock(
            email_enabled=True,
            in_app_enabled=False,
            achievement_notifs=True,
            inactivity_reminders=True,
            goal_notifs=True,
        )
        self.service.user_preferences_service = MagicMock(get_user_preferences=MagicMock(return_value=self.preferences))

    def _call(self, new_state, previous_state="ON_TRACK"):
        goal = make_goal()
        with patch("notifications.business.services.User.objects.get", return_value=self.recipient):
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
        with patch("notifications.business.services.User.objects.get", return_value=self.recipient):
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
        with patch("notifications.business.services.User.objects.get", return_value=user):
            result = service.list_recent(1)
        repo.list_recent.assert_called_once_with(user)
        assert result == repo.list_recent.return_value


class TestNotify:
    def setup_method(self):
        self.repo = MagicMock()
        self.user = MagicMock()
        self.preferences = MagicMock(
            email_enabled=True,
            in_app_enabled=False,
            achievement_notifs=True,
            inactivity_reminders=True,
            goal_notifs=True,
        )
        self.preference_service = MagicMock(get_user_preferences=MagicMock(return_value=self.preferences))
        self.service = NotificationService(repository=self.repo, user_preferences_service=self.preference_service)

    def test_notify_returns_none_when_all_channels_disabled(self):
        self.preferences.email_enabled = False
        self.preferences.in_app_enabled = False

        with patch("notifications.business.services.User.objects.get", return_value=self.user):
            result = self.service.notify("title", "desc", {"a": 1}, 1, NotificationType.MILESTONE_ACHIEVED)

        assert result is None
        self.repo.create_notification.assert_not_called()

    def test_notify_creates_notification_for_achievement(self):
        with patch("notifications.business.services.User.objects.get", return_value=self.user):
            result = self.service.notify("title", "desc", {"a": 1}, 1, NotificationType.MILESTONE_ACHIEVED)

        self.repo.create_notification.assert_called_once()
        assert result == self.repo.create_notification.return_value

    def test_mark_all_as_read_delegates_with_loaded_user(self):
        with patch("notifications.business.services.User.objects.get", return_value=self.user):
            self.service.mark_all_as_read(1)

        self.repo.mark_all_as_read.assert_called_once_with(self.user)


class TestUserPreferencesService:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = UserPreferencesService(repository=self.repo)
        self.user = MagicMock()

    def test_create_default_user_preferences_delegates(self):
        with patch("notifications.business.services.User.objects.get", return_value=self.user):
            result = self.service.create_default_user_preferences(1)

        self.repo.create_user_preferences.assert_called_once_with(self.user)
        assert result == self.repo.create_user_preferences.return_value

    def test_update_user_preferences_delegates(self):
        with patch("notifications.business.services.User.objects.get", return_value=self.user):
            result = self.service.update_user_preferences(1, email_enabled=False, goal_notifs=False)

        self.repo.update_user_preferences.assert_called_once_with(self.user, email_enabled=False, goal_notifs=False)
        assert result == self.repo.update_user_preferences.return_value

    def test_get_user_preferences_delegates(self):
        result = self.service.get_user_preferences(self.user)

        self.repo.get_user_preferences.assert_called_once_with(self.user)
        assert result == self.repo.get_user_preferences.return_value
