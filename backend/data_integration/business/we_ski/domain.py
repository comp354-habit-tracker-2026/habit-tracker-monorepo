from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class TrackPoint:
    """A single recorded point extracted from a We Ski GPX track."""

    time: Optional[datetime] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    ele: Optional[float] = None
    speed_mps: Optional[float] = None


@dataclass(frozen=True)
class ParsedSession:
    """Flattened parsed session compatible with the existing We Ski parser shape."""

    start_time: Optional[datetime]
    end_time: Optional[datetime]
    points: List[TrackPoint]
    bounds: Optional[Tuple[float, float, float, float]]
    track_name: Optional[str] = None