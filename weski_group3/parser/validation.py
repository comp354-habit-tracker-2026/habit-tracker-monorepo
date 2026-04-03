import json
from pathlib import Path
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, List, Tuple

from models import TrackPoint, ParsedSession


def load_parsed_session(json_path: str | Path) -> ParsedSession:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    points = [
        TrackPoint(
            time=datetime.fromisoformat(p["time"]) if p.get("time") else None,
            lat=p.get("lat"),
            lon=p.get("lon"),
            ele=p.get("ele"),
            speed_mps=p.get("speed_mps"),
        )
        for p in data.get("points", [])
    ]

    return ParsedSession(
        start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
        end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
        points=points,
        bounds=tuple(data["bounds"]) if data.get("bounds") else None,
        track_name=data.get("track_name"),
    )


def validate_session(
    session: ParsedSession,
    max_gap_seconds: int = 60,
    spike_far_meters: float = 80.0,
    spike_near_meters: float = 20.0,
) -> ParsedSession:
    clean_points: List[TrackPoint] = []
    points = session.points

    for i, p in enumerate(points):
        lat = p.lat
        lon = p.lon

        # missing coordinates -> try interpolation
        if lat is None or lon is None:
            lat, lon = _interpolate_coords(points, i, max_gap_seconds)

        # still missing -> drop
        if lat is None or lon is None:
            continue

        # out of range -> drop
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue

        temp_point = TrackPoint(
            time=p.time,
            lat=lat,
            lon=lon,
            ele=p.ele,
            speed_mps=p.speed_mps,
        )

        # spike point -> replace with interpolated coords, otherwise drop
        if _is_spike(points, i, temp_point, spike_far_meters, spike_near_meters, max_gap_seconds):
            new_lat, new_lon = _interpolate_coords(points, i, max_gap_seconds)
            if new_lat is None or new_lon is None:
                continue
            lat, lon = new_lat, new_lon

        clean_points.append(
            TrackPoint(
                time=p.time,
                lat=lat,
                lon=lon,
                ele=p.ele,
                speed_mps=p.speed_mps,
            )
        )

    start_time, end_time = _infer_time_bounds(clean_points)

    return ParsedSession(
        start_time=start_time,
        end_time=end_time,
        points=clean_points,
        bounds=_compute_bounds(clean_points),
        track_name=session.track_name,
    )


def _interpolate_coords(
    points: List[TrackPoint],
    i: int,
    max_gap_seconds: int,
) -> tuple[Optional[float], Optional[float]]:
    curr = points[i]

    if curr.time is None:
        return None, None

    prev_point = None
    next_point = None

    for j in range(i - 1, -1, -1):
        p = points[j]
        if p.time is not None and p.lat is not None and p.lon is not None:
            prev_point = p
            break

    for j in range(i + 1, len(points)):
        p = points[j]
        if p.time is not None and p.lat is not None and p.lon is not None:
            next_point = p
            break

    if prev_point is None or next_point is None:
        return None, None

    total_gap = (next_point.time - prev_point.time).total_seconds()
    if total_gap <= 0 or total_gap > max_gap_seconds:
        return None, None

    curr_gap = (curr.time - prev_point.time).total_seconds()
    ratio = curr_gap / total_gap

    lat = prev_point.lat + (next_point.lat - prev_point.lat) * ratio
    lon = prev_point.lon + (next_point.lon - prev_point.lon) * ratio
    return lat, lon


def _is_spike(
    points: List[TrackPoint],
    i: int,
    curr_point: TrackPoint,
    spike_far_meters: float,
    spike_near_meters: float,
    max_gap_seconds: int,
) -> bool:
    prev_point = None
    next_point = None

    for j in range(i - 1, -1, -1):
        p = points[j]
        if p.time is not None and p.lat is not None and p.lon is not None:
            prev_point = p
            break

    for j in range(i + 1, len(points)):
        p = points[j]
        if p.time is not None and p.lat is not None and p.lon is not None:
            next_point = p
            break

    if prev_point is None or next_point is None:
        return False
    if curr_point.lat is None or curr_point.lon is None or curr_point.time is None:
        return False

    total_gap = (next_point.time - prev_point.time).total_seconds()
    if total_gap <= 0 or total_gap > max_gap_seconds:
        return False

    d_prev_curr = _distance_m(prev_point.lat, prev_point.lon, curr_point.lat, curr_point.lon)
    d_curr_next = _distance_m(curr_point.lat, curr_point.lon, next_point.lat, next_point.lon)
    d_prev_next = _distance_m(prev_point.lat, prev_point.lon, next_point.lat, next_point.lon)

    return (
        d_prev_curr > spike_far_meters
        and d_curr_next > spike_far_meters
        and d_prev_next < spike_near_meters
    )


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0

    p1 = radians(lat1)
    p2 = radians(lat2)
    dp = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)

    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def save_session(session: ParsedSession, output_path: str | Path) -> None:
    def to_dict(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, list):
            return [to_dict(x) for x in obj]
        if isinstance(obj, tuple):
            return [to_dict(x) for x in obj]
        if hasattr(obj, "__dataclass_fields__"):
            return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
        return obj

    Path(output_path).write_text(
        json.dumps(to_dict(session), indent=2),
        encoding="utf-8",
    )


def _infer_time_bounds(points: List[TrackPoint]) -> tuple[Optional[datetime], Optional[datetime]]:
    times = [p.time for p in points if p.time is not None]
    if not times:
        return None, None
    return min(times), max(times)


def _compute_bounds(points: List[TrackPoint]) -> Optional[Tuple[float, float, float, float]]:
    lats = [p.lat for p in points if p.lat is not None]
    lons = [p.lon for p in points if p.lon is not None]
    if not lats or not lons:
        return None
    return (min(lats), min(lons), max(lats), max(lons))


if __name__ == "__main__":
    sessions_dir = Path(r"weski_group3\sessions")
    output_dir = sessions_dir / "validated"
    output_dir.mkdir(exist_ok=True)

    for input_file in sorted(sessions_dir.glob("*.json")):
        session = load_parsed_session(input_file)
        cleaned = validate_session(
            session,
            max_gap_seconds=60,
            spike_far_meters=80,
            spike_near_meters=20,
        )

        output_file = output_dir / input_file.name
        save_session(cleaned, output_file)

        print(f"{input_file.name}: {len(session.points)} -> {len(cleaned.points)} points")
        print(f"saved to: {output_file}")