from __future__ import annotations

from datetime import datetime
import math
import re
from typing import Any

from .domain import ParsedSession, TrackPoint


class WeSkiSessionTransformer:
    """Normalize parsed We Ski sessions into a payload suitable for downstream ingestion."""

    def normalize(self, session: ParsedSession) -> dict[str, Any]:
        total_distance_m = round(self._calculate_total_distance(session.points), 2)
        total_elevation_gain_m = round(self._calculate_elevation_gain(session.points), 2)
        duration_seconds = self._calculate_duration_seconds(
            session.start_time,
            session.end_time,
        )

        return {
            "provider": "we_ski",
            "activity_type": "ski",
            "external_id": self._build_external_id(session.track_name, session.start_time),
            "name": session.track_name,
            "source": "we_ski_gpx",
            "summary": {
                "point_count": len(session.points),
                "segment_count": 1 if session.points else 0,
                "started_at": self._isoformat(session.start_time),
                "ended_at": self._isoformat(session.end_time),
                "duration_seconds": duration_seconds,
                "total_distance_m": total_distance_m,
                "total_elevation_gain_m": total_elevation_gain_m,
                "bounds": session.bounds,
            },
            "track_name": session.track_name,
            "bounds": session.bounds,
            "points": [self._serialize_point(point) for point in session.points],
        }

    @staticmethod
    def _serialize_point(point: TrackPoint) -> dict[str, Any]:
        return {
            "time": WeSkiSessionTransformer._isoformat(point.time),
            "lat": point.lat,
            "lon": point.lon,
            "ele": point.ele,
            "speed_mps": point.speed_mps,
        }

    @staticmethod
    def _isoformat(value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None

    @staticmethod
    def _calculate_duration_seconds(started_at: datetime | None, ended_at: datetime | None) -> int | None:
        if started_at is None or ended_at is None:
            return None
        return int((ended_at - started_at).total_seconds())

    def _calculate_total_distance(self, points: list[TrackPoint]) -> float:
        if len(points) < 2:
            return 0.0

        total_distance = 0.0
        for previous, current in zip(points, points[1:]):
            total_distance += self._haversine_distance_m(previous, current)
        return total_distance

    @staticmethod
    def _calculate_elevation_gain(points: list[TrackPoint]) -> float:
        total_elevation_gain = 0.0
        for previous, current in zip(points, points[1:]):
            if previous.ele is None or current.ele is None:
                continue
            elevation_delta = current.ele - previous.ele
            if elevation_delta > 0:
                total_elevation_gain += elevation_delta
        return total_elevation_gain

    @staticmethod
    def _haversine_distance_m(first: TrackPoint, second: TrackPoint) -> float:
        if first.lat is None or first.lon is None or second.lat is None or second.lon is None:
            return 0.0

        earth_radius_m = 6_371_000
        latitude_delta = math.radians(second.lat - first.lat)
        longitude_delta = math.radians(second.lon - first.lon)
        first_latitude_radians = math.radians(first.lat)
        second_latitude_radians = math.radians(second.lat)

        haversine = (
            math.sin(latitude_delta / 2) ** 2
            + math.cos(first_latitude_radians)
            * math.cos(second_latitude_radians)
            * math.sin(longitude_delta / 2) ** 2
        )
        arc = 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))
        return earth_radius_m * arc

    @staticmethod
    def _build_external_id(track_name: str | None, started_at: datetime | None) -> str:
        timestamp = started_at.isoformat() if started_at else "undated"
        base_name = track_name or "session"
        slug = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-") or "session"
        return f"we-ski-{slug}-{timestamp}"