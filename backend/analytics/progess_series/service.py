from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Iterable
from .models import ProgressPoint, ProgressSeries



class ProgressSeriesError(Exception):
    """Base error for progress-series generation failures."""

class InvalidGranularityError(ProgressSeriesError):
    """Raised when a caller requests an unsupported bucket size."""

class UnsupportedGoalTypeError(ProgressSeriesError):
    """Raised when the goal metric cannot be derived from an activity."""


def _to_date(value: Any) -> date:
    """Normalize supported date-like values to a ``date`` instance."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise ValueError(f"Unsupported date value: {value}")


def _to_float(value: Any) -> float:
    """Convert numbers from model fields or serialized values to ``float``."""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _start_of_week(d: date) -> date:
    """Return the Monday for the week containing ``d``."""
    return d - timedelta(days=d.weekday())


def _daterange(start: date, end: date):
    """Yield each calendar day in the inclusive range [start, end]."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _weekrange(start: date, end: date):
    """Yield each week bucket start date covering [start, end]."""
    current = _start_of_week(start)
    last = _start_of_week(end)
    while current <= last:
        yield current
        current += timedelta(days=7)


def _resolve_metric_value(goal_type: str, activity: Any) -> float:
    """Map a goal type to the activity field used for accumulation."""
    if goal_type == "distance":
        return _to_float(activity.distance)
    if goal_type == "duration":
        return _to_float(activity.duration)
    if goal_type == "calories":
        return _to_float(activity.calories)
    if goal_type == "frequency":
        return 1.0

    raise UnsupportedGoalTypeError(
        f"Goal type '{goal_type}' is not supported for progress series."
    )


def generate_progress_series(
    goal: Any,
    activities: Iterable[Any],
    granularity: str = "daily",
) -> ProgressSeries:
    """
    Build chart-ready progress data for a goal.

    The returned payload is designed to support the kind of goal-vs-actual
    progress views described for Goal Progress Analytics in the project brief.
    It buckets activity data by day or week, computes cumulative totals, and
    returns summary fields that a frontend can render directly.
    """
    normalized_granularity = granularity.strip().lower()
    if normalized_granularity not in {"daily", "weekly"}:
        raise InvalidGranularityError("Granularity must be 'daily' or 'weekly'.")

    start_date = _to_date(goal.start_date)
    end_date = _to_date(goal.end_date)

    if end_date < start_date:
        raise ProgressSeriesError("Goal end_date cannot be before start_date.")

    # Aggregate metric values into date/week buckets.
    bucket_totals: dict[date, float] = defaultdict(float)

    for activity in activities:
        activity_date = _to_date(activity.date)

        # Ignore records that belong to a different user. This keeps the
        # service safe even if the queryset passed in is broader than expected.
        if getattr(activity, 'account_id', None):
            activity_user_id = activity.account.user_id
        else:
            activity_user_id = getattr(activity, 'user_id', None)
        if activity_user_id != goal.user_id:
            continue

        # Ignore out-of-range activity rows so callers can safely pass in an
        # unfiltered queryset if needed.
        if activity_date < start_date or activity_date > end_date:
            continue

        value = _resolve_metric_value(goal.goal_type, activity)
        bucket_key = (
            activity_date
            if normalized_granularity == "daily"
            else _start_of_week(activity_date)
        )
        bucket_totals[bucket_key] += value

    bucket_dates = (
        list(_daterange(start_date, end_date))
        if normalized_granularity == "daily"
        else list(_weekrange(start_date, end_date))
    )

    points: list[ProgressPoint] = []
    cumulative = 0.0

    for bucket_date in bucket_dates:
        value = round(bucket_totals.get(bucket_date, 0.0), 2)
        cumulative = round(cumulative + value, 2)

        # Weekly labels are explicit so the API is easier to consume in charts.
        label = (
            bucket_date.isoformat()
            if normalized_granularity == "daily"
            else f"week_of_{bucket_date.isoformat()}"
        )

        points.append(
            ProgressPoint(
                label=label,
                value=value,
                cumulative=cumulative,
            )
        )

    actual_value = round(sum(point.value for point in points), 2)
    target_value = round(_to_float(goal.target_value), 2)
    percent_complete = (
        round((actual_value / target_value) * 100, 2) if target_value > 0 else 0.0
    )

    return ProgressSeries(
        goal_id=goal.id,
        goal_title=goal.title,
        goal_type=goal.goal_type,
        granularity=normalized_granularity,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        target_value=target_value,
        actual_value=actual_value,
        percent_complete=percent_complete,
        no_data=actual_value == 0,
        points=points,
    )
