from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class StravaActivitySummary:
    """Summary of a Strava activity returned by the Strava activities API."""

    external_id: str
    name: str
    sport_type: str | None
    activity_type: str | None
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    start_date: datetime | None
    start_date_local: datetime | None
    timezone: str | None
    average_speed: float | None
    max_speed: float | None
    raw_data: dict[str, Any] = field(default_factory=dict)
