"""Unit tests for GoalService business logic.

These tests use mocks instead of the database so they run fast and
exercise the service in isolation from Django models.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from core.business import DomainValidationError
from goals.business.services import GoalService


def make_goal(
    pk=1,
    target_value=100,
    current_value=50,
    end_date=None,
):
    goal = MagicMock()
    goal.pk = pk
    goal.target_value = target_value
    goal.current_value = current_value
    goal.end_date = end_date
    return goal


class TestCoerceDecimal:
    def test_none_returns_none(self):
        assert GoalService._coerce_decimal(None) is None

    def test_integer_converts(self):
        assert GoalService._coerce_decimal(42) == Decimal("42")

    def test_float_converts(self):
        result = GoalService._coerce_decimal(3.14)
        assert isinstance(result, Decimal)

    def test_valid_string_converts(self):
        assert GoalService._coerce_decimal("99.5") == Decimal("99.5")

    def test_invalid_string_returns_none(self):
        assert GoalService._coerce_decimal("not-a-number") is None

    def test_invalid_type_returns_none(self):
        assert GoalService._coerce_decimal(object()) is None


class TestIsDeadlinePassed:
    def _now(self):
        return timezone.now()

    def test_past_date_returns_true(self):
        past_date = date.today() - timedelta(days=1)
        assert GoalService._is_deadline_passed(past_date, self._now()) is True

    def test_future_date_returns_false(self):
        future_date = date.today() + timedelta(days=1)
        assert GoalService._is_deadline_passed(future_date, self._now()) is False

    def test_today_returns_false(self):
        assert GoalService._is_deadline_passed(date.today(), self._now()) is False

    def test_past_aware_datetime_returns_true(self):
        past_dt = timezone.now() - timedelta(hours=1)
        assert GoalService._is_deadline_passed(past_dt, timezone.now()) is True

    def test_future_aware_datetime_returns_false(self):
        future_dt = timezone.now() + timedelta(hours=1)
        assert GoalService._is_deadline_passed(future_dt, timezone.now()) is False

    def test_naive_datetime_is_handled(self):
        past_naive = datetime.now() - timedelta(hours=1)
        assert GoalService._is_deadline_passed(past_naive, timezone.now()) is True

    def test_unsupported_type_returns_false(self):
        assert GoalService._is_deadline_passed("2020-01-01", timezone.now()) is False


class TestGetStatusSummary:
    def setup_method(self):
        self.service = GoalService(repository=MagicMock())

    # --- invalid target_value ---

    def test_negative_target_raises(self):
        goal = make_goal(target_value=-1)
        with pytest.raises(DomainValidationError):
            self.service.get_status_summary(goal)

    def test_non_numeric_target_raises(self):
        goal = make_goal(target_value="invalid")
        with pytest.raises(DomainValidationError):
            self.service.get_status_summary(goal)

    # --- missing / null actual_value ---

    def test_get_actual_value_exception_gives_at_risk(self):
        goal = make_goal(target_value=100)
        self.service.get_actual_value = MagicMock(side_effect=RuntimeError("no data"))
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_AT_RISK
        assert GoalService.MISSING_ACTUAL_NOTE in result["notes"]
        assert result["actualValue"] == 0.0

    def test_non_numeric_actual_gives_at_risk(self):
        goal = make_goal(target_value=100, current_value="bad")
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_AT_RISK
        assert GoalService.MISSING_ACTUAL_NOTE in result["notes"]

    # --- negative actual_value ---

    def test_negative_actual_clamped_to_zero(self):
        goal = make_goal(target_value=100, current_value=-10)
        result = self.service.get_status_summary(goal)
        assert result["actualValue"] == 0.0
        assert GoalService.NEGATIVE_ACTUAL_NOTE in result["notes"]
        assert result["status"] == GoalService.STATUS_AT_RISK

    # --- target_value == 0 ---

    def test_zero_target_is_achieved(self):
        goal = make_goal(target_value=0, current_value=0)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_ACHIEVED
        assert result["percentComplete"] == 100.0

    # --- actual >= target ---

    def test_actual_equals_target_is_achieved(self):
        goal = make_goal(target_value=100, current_value=100)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_ACHIEVED

    def test_actual_exceeds_target_is_achieved(self):
        goal = make_goal(target_value=100, current_value=150)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_ACHIEVED

    # --- deadline passed ---

    def test_missed_when_deadline_passed_and_below_target(self):
        past_date = date.today() - timedelta(days=1)
        goal = make_goal(target_value=100, current_value=50, end_date=past_date)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_MISSED

    # --- on track ---

    def test_on_track_when_at_75_percent(self):
        future = date.today() + timedelta(days=10)
        goal = make_goal(target_value=100, current_value=75, end_date=future)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_ON_TRACK

    def test_on_track_above_75_percent(self):
        future = date.today() + timedelta(days=10)
        goal = make_goal(target_value=100, current_value=90, end_date=future)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_ON_TRACK

    # --- at risk ---

    def test_at_risk_below_75_percent_with_future_deadline(self):
        future = date.today() + timedelta(days=10)
        goal = make_goal(target_value=100, current_value=40, end_date=future)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_AT_RISK

    def test_at_risk_below_75_percent_no_deadline(self):
        goal = make_goal(target_value=100, current_value=40, end_date=None)
        result = self.service.get_status_summary(goal)
        assert result["status"] == GoalService.STATUS_AT_RISK

    # --- payload structure ---

    def test_payload_has_expected_keys(self):
        goal = make_goal(target_value=100, current_value=80)
        result = self.service.get_status_summary(goal)
        for key in ("goalId", "actualValue", "targetValue", "percentComplete", "status", "evaluatedAt"):
            assert key in result

    def test_notes_absent_when_no_warnings(self):
        goal = make_goal(target_value=100, current_value=80)
        result = self.service.get_status_summary(goal)
        assert "notes" not in result

    def test_percent_complete_accuracy(self):
        goal = make_goal(target_value=3, current_value=1)
        result = self.service.get_status_summary(goal)
        assert result["percentComplete"] == pytest.approx(33.33, abs=0.01)


class TestProgressPercentage:
    def test_zero_target_returns_zero(self):
        assert GoalService.progress_percentage(50, 0) == Decimal("0")

    def test_none_target_returns_zero(self):
        assert GoalService.progress_percentage(50, None) == Decimal("0")

    def test_normal_progress(self):
        result = GoalService.progress_percentage(25, 100)
        assert result == Decimal("25")

    def test_capped_at_100(self):
        result = GoalService.progress_percentage(200, 100)
        assert result == Decimal("100")
