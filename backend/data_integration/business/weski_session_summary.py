from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class WeskiSessionSummary:
    """Summary of a parsed weSki GPX session with computed metrics."""

    external_id: str
    track_name: str | None
    start_time: datetime | None
    total_elevation_gain_meters: float
    total_distance_km: float
    number_of_runs: int
    total_time_seconds: float
    average_speed_kmh: float
    max_speed_kmh: float
    raw_data: dict[str, Any] = field(default_factory=dict)
