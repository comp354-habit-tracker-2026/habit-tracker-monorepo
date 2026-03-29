from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass
class Activity:
    activity_id: str
    user_id: str
    source: Literal["Strava", "MapMyRun", "WeSki", "MyWhoosh"]
    activity_type: Literal["RUN", "RIDE", "SWIM", "SKI", "SNOWBOARD", "WALK", "WORKOUT", "OTHER"]
    start_time: datetime
    duration_minutes: float
    distance_meters: float
    calories_kcal: float