from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, List, Literal

GoalType = Literal["weekly_distance", "weekly_duration", "daily_steps"]


@dataclass(frozen=True)
class Goal:
    id: str
    user_id: str
    type: GoalType
    target_value: int
    period_start: str
    period_end: Optional[str] = None


class GoalRepository(Protocol):
    def create_goal(self, user_id: str, payload: Goal) -> Goal:
        ...

    def list_goals(self, user_id: str) -> List[Goal]:
        ...

    def get_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        ...


class NotImplementedGoalRepository:
    def create_goal(self, user_id: str, payload: Goal) -> Goal:
        raise NotImplementedError("create_goal is not implemented")

    def list_goals(self, user_id: str) -> List[Goal]:
        raise NotImplementedError("list_goals is not implemented")

    def get_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        raise NotImplementedError("get_goal_by_id is not implemented")
