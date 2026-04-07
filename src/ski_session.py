from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class SkiSession:
    date: date
    duration: timedelta
    vertical_drop_meters: float
    distance_meters: float
    number_of_runs: int

    def __post_init__(self):
        if self.date is None:
            raise ValueError("date cannot be None")
        if self.duration is None:
            raise ValueError("duration cannot be None")
        if self.duration.total_seconds() < 0:
            raise ValueError("duration cannot be negative")
        if self.vertical_drop_meters < 0:
            raise ValueError("vertical_drop_meters cannot be negative")
        if self.distance_meters < 0:
            raise ValueError("distance_meters cannot be negative")
        if self.number_of_runs < 0:
            raise ValueError("number_of_runs cannot be negative")