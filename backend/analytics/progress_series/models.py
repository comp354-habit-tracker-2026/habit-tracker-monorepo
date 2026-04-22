from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class ProgressPoint:
    """Single point in the returned chart series."""

    label: str
    value: float
    cumulative: float

@dataclass
class PaginationMeta:
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }


@dataclass
class ProgressSeries:
    goal_id: int
    goal_title: str
    goal_type: str
    granularity: str
    start_date: str
    end_date: str
    target_value: float
    actual_value: float
    percent_complete: float
    no_data: bool
    points: List[ProgressPoint]
    pagination: PaginationMeta | None = None

    def to_dict(self) -> dict:
        return {
            "goal_id": self.goal_id,
            "goal_title": self.goal_title,
            "goal_type": self.goal_type,
            "granularity": self.granularity,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "target_value": self.target_value,
            "actual_value": self.actual_value,
            "percent_complete": self.percent_complete,
            "no_data": self.no_data,
            "pagination": self.pagination.to_dict() if self.pagination else None,
            "points": [
                {
                    "label": p.label,
                    "value": p.value,
                    "cumulative": p.cumulative,
                }
                for p in self.points
            ],
        }

@dataclass
class DemoGoal:
    """goal used for quick manual endpoint testing."""

    id: int
    title: str
    goal_type: str
    target_value: float
    start_date: date
    end_date: date
    user_id: int


@dataclass
class DemoActivity:
    """activity used for quick manual endpoint testing."""

    date: date
    distance: float = 0.0
    duration: float = 0.0
    calories: float = 0.0
    user_id: int = 1
    account_id: int = None
