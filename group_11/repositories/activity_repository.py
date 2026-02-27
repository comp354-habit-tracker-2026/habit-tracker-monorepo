from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, List, Generic, TypeVar, Literal

T = TypeVar("T")

Provider = Literal["strava", "mapmyrun", "weski", "mywhoosh", "manual"]
ActivityType = Literal["run", "ride", "ski", "walk", "workout"]


@dataclass(frozen=True)
class Activity:
    id: str
    user_id: str
    provider: Provider
    external_id: str
    type: ActivityType
    start_time: str
    duration_seconds: int
    distance_meters: Optional[int] = None
    calories: Optional[int] = None


@dataclass(frozen=True)
class Page(Generic[T]):
    items: List[T]
    limit: int
    offset: int
    total: Optional[int] = None


class ActivityRepository(Protocol):
    def upsert_activity_by_source(
        self,
        user_id: str,
        provider: Provider,
        external_id: str,
        payload: Activity,
    ) -> Activity:
        """
        Dedup key is (provider, external_id).
        If the same key appears again, update the existing record.
        """
        ...

    def list_activities(
        self,
        user_id: str,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[Activity]:
        ...

    def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        ...


class NotImplementedActivityRepository:
    def upsert_activity_by_source(
        self, user_id: str, provider: Provider, external_id: str, payload: Activity
    ) -> Activity:
        raise NotImplementedError("upsert_activity_by_source is not implemented")

    def list_activities(
        self,
        user_id: str,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[Activity]:
        raise NotImplementedError("list_activities is not implemented")

    def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        raise NotImplementedError("get_activity_by_id is not implemented")
