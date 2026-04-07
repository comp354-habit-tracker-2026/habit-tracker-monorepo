from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

class ActivitySource(StrEnum):
    STRAVA = "Strava"
    MAP_MY_RUN = "MapMyRun"
    WE_SKI = "WeSki"
    MY_WHOOSH = "MyWhoosh"

class ActivityType(StrEnum):
    RUN = "RUN"
    RIDE = "RIDE"
    SWIM = "SWIM"
    SKI = "SKI"
    SNOWBOARD = "SNOWBOARD"
    WALK = "WALK"
    WORKOUT = "WORKOUT"
    OTHER = "OTHER"

@dataclass
class Activity:
    activity_id: str
    user_id: str
    source: ActivitySource
    activity_type: ActivityType
    start_time: datetime
    duration_minutes: float
    distance_meters: float
    calories_kcal: float
    

# Placeholders

class MyWhooshActivity(Activity):
    pass

class StravaActivity(Activity):
    pass

class WeSkiActivity(Activity):
    pass

class MapMyRunActivity(Activity):
    pass