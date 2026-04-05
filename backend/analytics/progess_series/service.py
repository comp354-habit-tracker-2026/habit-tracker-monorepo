from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Iterable


class ProgressSeriesError(Exception):
    """Base error for progress-series generation failures."""

class InvalidGranularityError(ProgressSeriesError):
    """Raised when a caller requests an unsupported bucket size."""

class UnsupportedGoalTypeError(ProgressSeriesError):
    """Raised when the goal metric cannot be derived from an activity."""



@dataclass
class ProgressPoint:
    label: str
    value: float
    cumulative: float


def _to_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise ValueError(f"Unsupported date value: {value}")


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _weekrange(start: date, end: date):
    current = _start_of_week(start)
    last = _start_of_week(end)
    while current <= last:
        yield current
        current += timedelta(days=7)


def _resolve_metric_value(goal_type: str, activity: Any) -> float:
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


def generate_progress_series(goal: Any, activities: Iterable[Any], granularity: str = "daily") -> dict[str, Any]:
    if granularity not in {"daily", "weekly"}:
        raise InvalidGranularityError("Granularity must be 'daily' or 'weekly'.")

    start_date = _to_date(goal.start_date)
    end_date = _to_date(goal.end_date)

    if end_date < start_date:
        raise ProgressSeriesError("Goal end_date cannot be before start_date.")

    bucket_totals: dict[date, float] = defaultdict(float)

    for activity in activities:
        activity_date = _to_date(activity.date)

        if activity.user_id != goal.user_id:
            continue

        if activity_date < start_date or activity_date > end_date:
            continue

        value = _resolve_metric_value(goal.goal_type, activity)

        if granularity == "daily":
            bucket_key = activity_date
        else:
            bucket_key = _start_of_week(activity_date)

        bucket_totals[bucket_key] += value

    bucket_dates = list(_daterange(start_date, end_date)) if granularity == "daily" else list(_weekrange(start_date, end_date))

    points: list[ProgressPoint] = []
    cumulative = 0.0

    for bucket_date in bucket_dates:
        value = round(bucket_totals.get(bucket_date, 0.0), 2)
        cumulative = round(cumulative + value, 2)

        label = bucket_date.isoformat() if granularity == "daily" else f"{bucket_date.isoformat()}_week"

        points.append(
            ProgressPoint(
                label=label,
                value=value,
                cumulative=cumulative,
            )
        )

    actual_value = round(sum(point.value for point in points), 2)
    target_value = round(_to_float(goal.target_value), 2)
    percent_complete = round((actual_value / target_value) * 100, 2) if target_value > 0 else 0.0

    return {
        "goal_id": goal.id,
        "goal_title": goal.title,
        "goal_type": goal.goal_type,
        "granularity": granularity,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "target_value": target_value,
        "actual_value": actual_value,
        "percent_complete": percent_complete,
        "no_data": actual_value == 0,
        "points": [
            {
                "label": point.label,
                "value": point.value,
                "cumulative": point.cumulative,
            }
            for point in points
        ],
    }