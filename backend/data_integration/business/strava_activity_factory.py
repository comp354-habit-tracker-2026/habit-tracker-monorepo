from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

from .strava_activity_summary import StravaActivitySummary


class StravaActivityFactory:
    """Builds Strava activity summaries from raw Strava API payloads."""

    @classmethod
    def create_activity_summary(cls, raw_activity: Mapping[str, Any]) -> StravaActivitySummary:
        external_id = str(raw_activity["id"])

        return StravaActivitySummary(
            external_id=external_id,
            name=str(raw_activity.get("name", "")),
            sport_type=cls._coerce_optional_string(raw_activity.get("sport_type")),
            activity_type=cls._coerce_optional_string(raw_activity.get("type")),
            distance=cls._coerce_float(raw_activity.get("distance")),
            moving_time=cls._coerce_int(raw_activity.get("moving_time")),
            elapsed_time=cls._coerce_int(raw_activity.get("elapsed_time")),
            total_elevation_gain=cls._coerce_float(raw_activity.get("total_elevation_gain")),
            start_date=cls._parse_datetime(raw_activity.get("start_date")),
            start_date_local=cls._parse_datetime(raw_activity.get("start_date_local")),
            timezone=cls._coerce_optional_string(raw_activity.get("timezone")),
            average_speed=cls._coerce_optional_float(raw_activity.get("average_speed")),
            max_speed=cls._coerce_optional_float(raw_activity.get("max_speed")),
            raw_data=dict(raw_activity),
        )

    @classmethod
    def create_activity_summaries(
        cls,
        raw_activities: Iterable[Mapping[str, Any]],
    ) -> list[StravaActivitySummary]:
        return [cls.create_activity_summary(raw_activity) for raw_activity in raw_activities]

    @classmethod
    def create_many(cls, raw_activities: Iterable[Mapping[str, Any]]) -> list[StravaActivitySummary]:
        return cls.create_activity_summaries(raw_activities)

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        normalized = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)

    @staticmethod
    def _coerce_int(value: Any) -> int:
        if value in (None, ""):
            return 0
        return int(value)

    @staticmethod
    def _coerce_float(value: Any) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    @staticmethod
    def _coerce_optional_float(value: Any) -> float | None:
        if value in (None, ""):
            return None
        return float(value)

    @staticmethod
    def _coerce_optional_string(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value)
