from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from threading import Lock
from typing import Callable

from .models import ProgressSeries


@dataclass(frozen=True)
class ProgressSeriesCacheKey:
    goal_id: int
    granularity: str
    provider: str | None
    activity_version: int


class ActivityProgressVersionStore:
    """Track activity revisions per user so cached progress can be refreshed."""

    def __init__(self):
        self._versions: dict[int, int] = {}
        self._lock = Lock()

    def get(self, user_id: int) -> int:
        with self._lock:
            return self._versions.get(user_id, 0)

    def bump(self, user_id: int) -> int:
        with self._lock:
            next_version = self._versions.get(user_id, 0) + 1
            self._versions[user_id] = next_version
            return next_version


class GoalProgressCache:
    """Small in-memory cache for goal progress series results."""

    def __init__(self, version_store: ActivityProgressVersionStore | None = None):
        self._version_store = version_store or ActivityProgressVersionStore()
        self._entries: dict[ProgressSeriesCacheKey, ProgressSeries] = {}
        self._lock = Lock()

    def build_key(
        self,
        *,
        goal_id: int,
        user_id: int,
        granularity: str,
        provider: str | None,
    ) -> ProgressSeriesCacheKey:
        return ProgressSeriesCacheKey(
            goal_id=goal_id,
            granularity=granularity,
            provider=provider,
            activity_version=self._version_store.get(user_id),
        )

    def get_or_compute(
        self,
        *,
        goal_id: int,
        user_id: int,
        granularity: str,
        provider: str | None,
        producer: Callable[[], ProgressSeries],
    ) -> ProgressSeries:
        key = self.build_key(
            goal_id=goal_id,
            user_id=user_id,
            granularity=granularity,
            provider=provider,
        )

        with self._lock:
            cached = self._entries.get(key)
        if cached is not None:
            return deepcopy(cached)

        computed = producer()
        with self._lock:
            self._entries[key] = deepcopy(computed)
        return computed

    def invalidate_for_user(self, user_id: int):
        self._version_store.bump(user_id)


goal_progress_cache = GoalProgressCache()
