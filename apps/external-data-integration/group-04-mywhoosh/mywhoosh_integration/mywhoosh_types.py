from dataclasses import dataclass
from typing import Optional, Any
from datetime import date

@dataclass
class Metrics: 
    distance: Optional[float] = None
    calories: Optional[int] = None
    duration: Optional[int] = None
   

@dataclass
class DataQuality:
    has_missing_value: bool
    source: str = "mywhoosh"

@dataclass
class NormalizedSession:
    activity_type: str
    date: date 
    provider: str = "mywhoosh"
    external_id: Optional[str] = None
    metrics: Optional[Metrics] = None
    data_quality: Optional[DataQuality] = None
    raw_data: Optional[dict[str, Any]] = None
