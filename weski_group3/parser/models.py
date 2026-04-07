from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple

@dataclass(frozen=True)
class TrackPoint:
    time: Optional[datetime] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    ele: Optional[float] = None
    speed_mps: Optional[float] = None

@dataclass(frozen=True)
class ParsedSession:
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    points: List[TrackPoint]
    bounds: Optional[Tuple[float,float,float,float]] # (min_lat,min_lon, max_lat, min_lat)
    track_name: Optional[str] = None

