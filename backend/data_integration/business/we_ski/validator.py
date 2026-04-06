from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt

from core.business.exceptions import DomainValidationError
from .domain import ParsedSession, TrackPoint


class WeSkiGpxValidator:
    """Clean and validate parsed GPX points."""

    def validate(
        self,
        session: ParsedSession,
        max_gap_seconds: int = 60,
        spike_far_meters: float = 80.0,
        spike_near_meters: float = 20.0,
    ) -> ParsedSession:
        points = self._clean_points(
            session.points,
            max_gap_seconds=max_gap_seconds,
            spike_far_meters=spike_far_meters,
            spike_near_meters=spike_near_meters,
        )

        if len(points) < 2:
            raise DomainValidationError(
                "A ski session requires at least two valid track points.",
                code="insufficient_track_points",
            )

        times = [p.time for p in points if p.time is not None]
        if times and times != sorted(times):
            raise DomainValidationError(
                "Track points must be ordered chronologically.",
                code="timestamps_out_of_order",
            )

        return ParsedSession(
            start_time=min(times) if times else None,
            end_time=max(times) if times else None,
            points=points,
            bounds=self._compute_bounds(points),
            track_name=session.track_name,
        )

    def _clean_points(
        self,
        points: list[TrackPoint],
        max_gap_seconds: int,
        spike_far_meters: float,
        spike_near_meters: float,
    ) -> list[TrackPoint]:
        cleaned: list[TrackPoint] = []

        for index, point in enumerate(points):
            lat, lon = point.lat, point.lon

            if lat is None or lon is None:
                lat, lon = self._interpolate_coords(points, index, max_gap_seconds)

            if lat is None or lon is None:
                continue

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue

            candidate = TrackPoint(
                time=point.time,
                lat=lat,
                lon=lon,
                ele=point.ele,
                speed_mps=point.speed_mps,
            )

            if self._is_spike(
                points,
                index,
                candidate,
                spike_far_meters,
                spike_near_meters,
                max_gap_seconds,
            ):
                lat, lon = self._interpolate_coords(points, index, max_gap_seconds)
                if lat is None or lon is None:
                    continue

                candidate = TrackPoint(
                    time=point.time,
                    lat=lat,
                    lon=lon,
                    ele=point.ele,
                    speed_mps=point.speed_mps,
                )

            cleaned.append(candidate)

        return cleaned

    @staticmethod
    def _interpolate_coords(
        points: list[TrackPoint],
        index: int,
        max_gap_seconds: int,
    ) -> tuple[float | None, float | None]:
        current = points[index]
        if current.time is None:
            return None, None

        prev_point = next(
            (
                p for p in reversed(points[:index])
                if p.time is not None and p.lat is not None and p.lon is not None
            ),
            None,
        )
        next_point = next(
            (
                p for p in points[index + 1:]
                if p.time is not None and p.lat is not None and p.lon is not None
            ),
            None,
        )

        if prev_point is None or next_point is None:
            return None, None

        total_gap = (next_point.time - prev_point.time).total_seconds()
        if total_gap <= 0 or total_gap > max_gap_seconds:
            return None, None

        ratio = (current.time - prev_point.time).total_seconds() / total_gap
        lat = prev_point.lat + (next_point.lat - prev_point.lat) * ratio
        lon = prev_point.lon + (next_point.lon - prev_point.lon) * ratio
        return lat, lon

    def _is_spike(
        self,
        points: list[TrackPoint],
        index: int,
        current: TrackPoint,
        spike_far_meters: float,
        spike_near_meters: float,
        max_gap_seconds: int,
    ) -> bool:
        if current.time is None or current.lat is None or current.lon is None:
            return False

        prev_point = next(
            (
                p for p in reversed(points[:index])
                if p.time is not None and p.lat is not None and p.lon is not None
            ),
            None,
        )
        next_point = next(
            (
                p for p in points[index + 1:]
                if p.time is not None and p.lat is not None and p.lon is not None
            ),
            None,
        )

        if prev_point is None or next_point is None:
            return False

        total_gap = (next_point.time - prev_point.time).total_seconds()
        if total_gap <= 0 or total_gap > max_gap_seconds:
            return False

        d1 = self._distance_m(prev_point.lat, prev_point.lon, current.lat, current.lon)
        d2 = self._distance_m(current.lat, current.lon, next_point.lat, next_point.lon)
        d3 = self._distance_m(prev_point.lat, prev_point.lon, next_point.lat, next_point.lon)

        return d1 > spike_far_meters and d2 > spike_far_meters and d3 < spike_near_meters

    @staticmethod
    def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6_371_000.0
        p1 = radians(lat1)
        p2 = radians(lat2)
        dp = radians(lat2 - lat1)
        dl = radians(lon2 - lon1)

        a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
        return r * 2 * atan2(sqrt(a), sqrt(1 - a))

    @staticmethod
    def _compute_bounds(points: list[TrackPoint]) -> tuple[float, float, float, float] | None:
        lats = [p.lat for p in points if p.lat is not None]
        lons = [p.lon for p in points if p.lon is not None]
        if not lats or not lons:
            return None
        return (min(lats), min(lons), max(lats), max(lons))