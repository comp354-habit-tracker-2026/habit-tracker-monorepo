from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any

from .weski_session_summary import WeskiSessionSummary

NS = {"gpx": "http://www.topografix.com/GPX/1/1"}


# ---------------------------------------------------------------------------
# Internal data structures (not exposed outside this module)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _TrackPoint:
    time: datetime | None = None
    lat: float | None = None
    lon: float | None = None
    ele: float | None = None
    speed_mps: float | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class WeskiGpxParser:
    """Parses a weSki GPX file and returns a WeskiSessionSummary."""

    @classmethod
    def parse(cls, gpx_content: str | bytes) -> WeskiSessionSummary:
        """Parse raw GPX content (string or bytes) into a session summary."""
        if isinstance(gpx_content, bytes):
            # Handle BOM
            gpx_content = gpx_content.decode("utf-8-sig")

        root = ET.fromstring(gpx_content)
        track_name = cls._text_or_none(root.find("gpx:trk/gpx:name", NS))
        points = cls._extract_points(root)
        clean_points = cls._validate_points(points)
        metrics = cls._calculate_metrics(clean_points, track_name)

        # Generate a stable external_id from content hash
        content_hash = hashlib.sha256(gpx_content.encode("utf-8")).hexdigest()[:16]
        external_id = f"weski-{content_hash}"

        return WeskiSessionSummary(
            external_id=external_id,
            track_name=track_name,
            start_time=metrics["start_time"],
            total_elevation_gain_meters=metrics["total_elevation_gain_meters"],
            total_distance_km=metrics["total_distance_km"],
            number_of_runs=metrics["number_of_runs"],
            total_time_seconds=metrics["total_time_seconds"],
            average_speed_kmh=metrics["average_speed_kmh"],
            max_speed_kmh=metrics["max_speed_kmh"],
            raw_data=metrics,
        )

    @classmethod
    def parse_file(cls, gpx_path: str | Path) -> WeskiSessionSummary:
        """Parse a GPX file from disk."""
        gpx_content = Path(gpx_path).read_text(encoding="utf-8-sig")
        return cls.parse(gpx_content)

    # ------------------------------------------------------------------
    # GPX extraction
    # ------------------------------------------------------------------

    @classmethod
    def _extract_points(cls, root: ET.Element) -> list[_TrackPoint]:
        points: list[_TrackPoint] = []
        for trkpt in root.findall(".//gpx:trkpt", NS):
            lat = cls._float_or_none(trkpt.attrib.get("lat"))
            lon = cls._float_or_none(trkpt.attrib.get("lon"))
            ele = cls._float_or_none(cls._text_or_none(trkpt.find("gpx:ele", NS)))
            speed = cls._float_or_none(cls._text_or_none(trkpt.find("gpx:speed", NS)))
            time = cls._dt_or_none(cls._text_or_none(trkpt.find("gpx:time", NS)))
            points.append(_TrackPoint(time=time, lat=lat, lon=lon, ele=ele, speed_mps=speed))
        return points

    # ------------------------------------------------------------------
    # Validation / cleaning
    # ------------------------------------------------------------------

    @classmethod
    def _validate_points(
        cls,
        points: list[_TrackPoint],
        max_gap_seconds: int = 60,
        spike_far_meters: float = 80.0,
        spike_near_meters: float = 20.0,
    ) -> list[_TrackPoint]:
        clean: list[_TrackPoint] = []
        for i, p in enumerate(points):
            lat, lon = p.lat, p.lon

            if lat is None or lon is None:
                lat, lon = cls._interpolate_coords(points, i, max_gap_seconds)

            if lat is None or lon is None:
                continue

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue

            temp = _TrackPoint(time=p.time, lat=lat, lon=lon, ele=p.ele, speed_mps=p.speed_mps)

            if cls._is_spike(points, i, temp, spike_far_meters, spike_near_meters, max_gap_seconds):
                new_lat, new_lon = cls._interpolate_coords(points, i, max_gap_seconds)
                if new_lat is None or new_lon is None:
                    continue
                lat, lon = new_lat, new_lon

            clean.append(_TrackPoint(time=p.time, lat=lat, lon=lon, ele=p.ele, speed_mps=p.speed_mps))

        return clean

    @classmethod
    def _interpolate_coords(
        cls,
        points: list[_TrackPoint],
        i: int,
        max_gap_seconds: int,
    ) -> tuple[float | None, float | None]:
        curr = points[i]
        if curr.time is None:
            return None, None

        prev_pt = next_pt = None
        for j in range(i - 1, -1, -1):
            p = points[j]
            if p.time is not None and p.lat is not None and p.lon is not None:
                prev_pt = p
                break
        for j in range(i + 1, len(points)):
            p = points[j]
            if p.time is not None and p.lat is not None and p.lon is not None:
                next_pt = p
                break

        if prev_pt is None or next_pt is None:
            return None, None

        total_gap = (next_pt.time - prev_pt.time).total_seconds()
        if total_gap <= 0 or total_gap > max_gap_seconds:
            return None, None

        ratio = (curr.time - prev_pt.time).total_seconds() / total_gap
        lat = prev_pt.lat + (next_pt.lat - prev_pt.lat) * ratio
        lon = prev_pt.lon + (next_pt.lon - prev_pt.lon) * ratio
        return lat, lon

    @classmethod
    def _is_spike(
        cls,
        points: list[_TrackPoint],
        i: int,
        curr: _TrackPoint,
        spike_far: float,
        spike_near: float,
        max_gap_seconds: int,
    ) -> bool:
        prev_pt = next_pt = None
        for j in range(i - 1, -1, -1):
            p = points[j]
            if p.time is not None and p.lat is not None and p.lon is not None:
                prev_pt = p
                break
        for j in range(i + 1, len(points)):
            p = points[j]
            if p.time is not None and p.lat is not None and p.lon is not None:
                next_pt = p
                break

        if prev_pt is None or next_pt is None:
            return False
        if curr.lat is None or curr.lon is None or curr.time is None:
            return False

        total_gap = (next_pt.time - prev_pt.time).total_seconds()
        if total_gap <= 0 or total_gap > max_gap_seconds:
            return False

        d_pc = cls._distance_m(prev_pt.lat, prev_pt.lon, curr.lat, curr.lon)
        d_cn = cls._distance_m(curr.lat, curr.lon, next_pt.lat, next_pt.lon)
        d_pn = cls._distance_m(prev_pt.lat, prev_pt.lon, next_pt.lat, next_pt.lon)

        return d_pc > spike_far and d_cn > spike_far and d_pn < spike_near

    # ------------------------------------------------------------------
    # Metrics calculation
    # ------------------------------------------------------------------

    @classmethod
    def _calculate_metrics(
        cls,
        points: list[_TrackPoint],
        track_name: str | None,
    ) -> dict[str, Any]:
        if not points:
            return {
                "track_name": track_name,
                "start_time": None,
                "total_elevation_gain_meters": 0.0,
                "total_distance_km": 0.0,
                "number_of_runs": 0,
                "total_time_seconds": 0.0,
                "average_speed_kmh": 0.0,
                "max_speed_kmh": 0.0,
            }

        total_distance_m = 0.0
        total_elevation_gain = 0.0
        max_speed_mps = 0.0
        speeds_mps: list[float] = []
        number_of_runs = 0
        current_state = "IDLE"

        RUN_SPEED_THRESHOLD = 2.5  # m/s
        ELEVATION_CHANGE_THRESHOLD = 5  # meters

        for i in range(1, len(points)):
            p1, p2 = points[i - 1], points[i]

            if any(
                v is None
                for v in (p1.lat, p1.lon, p1.ele, p1.speed_mps, p2.lat, p2.lon, p2.ele, p2.speed_mps)
            ):
                continue

            segment_dist = cls._distance_m(p1.lat, p1.lon, p2.lat, p2.lon)
            elev_change = p2.ele - p1.ele
            speed = p2.speed_mps

            # State machine for run counting
            if current_state in ("IDLE", "LIFT"):
                if elev_change < -ELEVATION_CHANGE_THRESHOLD and speed > RUN_SPEED_THRESHOLD:
                    current_state = "RUN"
                    number_of_runs += 1
            elif current_state == "RUN":
                if elev_change > ELEVATION_CHANGE_THRESHOLD:
                    current_state = "LIFT"

            total_distance_m += segment_dist
            if elev_change > 0:
                total_elevation_gain += elev_change
            speeds_mps.append(speed)
            if speed > max_speed_mps:
                max_speed_mps = speed

        times = [p.time for p in points if p.time is not None]
        start_time = min(times) if times else None
        end_time = max(times) if times else None
        total_seconds = (end_time - start_time).total_seconds() if start_time and end_time else 0.0

        mps_to_kmh = 3.6
        avg_speed = (sum(speeds_mps) / len(speeds_mps)) * mps_to_kmh if speeds_mps else 0.0

        return {
            "track_name": track_name,
            "start_time": start_time,
            "total_elevation_gain_meters": total_elevation_gain,
            "total_distance_km": total_distance_m / 1000,
            "number_of_runs": number_of_runs,
            "total_time_seconds": total_seconds,
            "average_speed_kmh": avg_speed,
            "max_speed_kmh": max_speed_mps * mps_to_kmh,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000.0
        p1, p2 = radians(lat1), radians(lat2)
        dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
        a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
        return r * 2 * atan2(sqrt(a), sqrt(1 - a))

    @staticmethod
    def _text_or_none(element: ET.Element | None) -> str | None:
        if element is None or element.text is None:
            return None
        return element.text.strip()

    @staticmethod
    def _float_or_none(txt: str | None) -> float | None:
        if txt is None or txt == "":
            return None
        try:
            return float(txt)
        except ValueError:
            return None

    @staticmethod
    def _dt_or_none(dt: str | None) -> datetime | None:
        if dt is None or dt == "":
            return None
        s = dt.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return None
