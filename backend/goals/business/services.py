from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.utils import timezone

from core.business import BaseService, DomainValidationError
from goals.data import GoalRepository


class GoalService(BaseService):
    STATUS_ON_TRACK = "ON_TRACK"
    STATUS_AT_RISK = "AT_RISK"
    STATUS_ACHIEVED = "ACHIEVED"
    STATUS_MISSED = "MISSED"
    ON_TRACK_THRESHOLD = Decimal("75")
    PERCENT_MULTIPLIER = Decimal("100")
    PERCENT_QUANTIZER = Decimal("0.01")
    MISSING_ACTUAL_NOTE = "Actual value unavailable; defaulted to 0 for status evaluation."
    NEGATIVE_ACTUAL_NOTE = "Negative actual value was clamped to 0."

    def __init__(self, repository=None):
        self.repository = repository or GoalRepository()

    def get_user_queryset(self, user, params):
        if user.is_staff or user.is_superuser:
            queryset = self.repository.model.objects.all().order_by("-created_at")
        else:
            queryset = self.repository.for_user(user)
        return self.repository.apply_filters(queryset, params)

    @staticmethod
    def progress_percentage(current_value, target_value):
        if target_value and target_value > 0:
            return min(Decimal("100"), (current_value / target_value) * 100)
        return Decimal("0")

    def get_user_goal(self, user, goal_id):
        return self.repository.for_user(user).filter(pk=goal_id).first()

    def get_actual_value(self, goal):
        """Retrieve actual progress value for a goal.

        Kept as a dedicated method so future integrations can source metrics
        externally without changing status computation code.
        """
        return goal.current_value

    def get_status_summary(self, goal):
        evaluated_at = timezone.now()
        notes = []

        target_value = self._coerce_decimal(goal.target_value)
        if target_value is None or target_value < 0:
            raise DomainValidationError(
                "Goal target value must be a non-negative number.",
                code="goal_invalid",
            )

        try:
            actual_value = self.get_actual_value(goal)
        except Exception:
            actual_value = None

        actual_value = self._coerce_decimal(actual_value)
        if actual_value is None:
            notes.append(self.MISSING_ACTUAL_NOTE)
            return self._build_status_payload(
                goal_id=goal.pk,
                actual_value=Decimal("0"),
                target_value=target_value,
                percent_complete=Decimal("0"),
                status=self.STATUS_AT_RISK,
                evaluated_at=evaluated_at,
                notes=notes,
            )

        if actual_value < 0:
            actual_value = Decimal("0")
            notes.append(self.NEGATIVE_ACTUAL_NOTE)

        if target_value == 0:
            percent_raw = Decimal("100")
            status = self.STATUS_ACHIEVED
        else:
            percent_raw = (actual_value / target_value) * self.PERCENT_MULTIPLIER

            if actual_value >= target_value:
                status = self.STATUS_ACHIEVED
            elif goal.end_date and self._is_deadline_passed(goal.end_date, evaluated_at):
                status = self.STATUS_MISSED
            elif percent_raw >= self.ON_TRACK_THRESHOLD:
                status = self.STATUS_ON_TRACK
            else:
                status = self.STATUS_AT_RISK

        percent_complete = self._round_percent(percent_raw)
        return self._build_status_payload(
            goal_id=goal.pk,
            actual_value=actual_value,
            target_value=target_value,
            percent_complete=percent_complete,
            status=status,
            evaluated_at=evaluated_at,
            notes=notes,
        )

    @classmethod
    def _round_percent(cls, percent_value):
        return percent_value.quantize(cls.PERCENT_QUANTIZER, rounding=ROUND_HALF_UP)

    @staticmethod
    def _coerce_decimal(value):
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None

    @staticmethod
    def _is_deadline_passed(deadline, evaluated_at):
        if isinstance(deadline, datetime):
            if timezone.is_naive(deadline):
                deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
            return evaluated_at > deadline

        if isinstance(deadline, date):
            return evaluated_at.date() > deadline

        return False

    @staticmethod
    def _build_status_payload(
        goal_id,
        actual_value,
        target_value,
        percent_complete,
        status,
        evaluated_at,
        notes,
    ):
        payload = {
            "goalId": goal_id,
            "actualValue": float(actual_value),
            "targetValue": float(target_value),
            "percentComplete": float(percent_complete),
            "status": status,
            "evaluatedAt": evaluated_at.isoformat(),
        }
        if notes:
            payload["notes"] = "; ".join(notes)
        return payload
