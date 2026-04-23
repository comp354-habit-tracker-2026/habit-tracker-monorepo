import asyncio
import inspect
import time
from datetime import datetime, timezone

from group_11.db.connection import db
from group_11.repositories.user_repository import UserRepository
from group_11.repositories.activity_repository import ActivityRepository
from group_11.repositories.goal_repository import GoalRepository


def _utc_iso(dt: datetime) -> str:
    # timezone-aware UTC ISO string (no utcnow deprecation)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _call_with_supported_kwargs(func, **kwargs):
    sig = inspect.signature(func)
    allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return func(**allowed)


# User (this script) -> Controller -> Repository -> Database
class UserController:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, email: str, name: str):
        print("Controller(User): create_user")
        return _call_with_supported_kwargs(self.repo.create_user, email=email, name=name)


class ActivityController:
    def __init__(self, repo: ActivityRepository):
        self.repo = repo

    def upsert_activity(
        self,
        user_id: str,
        provider: str,
        external_id: str,
        name: str,
        activity_type: str,
        start_time: str,
        duration_seconds: int,
        distance_meters=None,
        calories=None,
    ):
        print("Controller(Activity): upsert_activity_by_source")
        return _call_with_supported_kwargs(
            self.repo.upsert_activity_by_source,
            user_id=user_id,
            provider=provider,
            external_id=external_id,
            name=name,
            activity_type=activity_type,
            type=activity_type,  # in case repo uses `type`
            start_time=start_time,
            duration_seconds=duration_seconds,
            distance_meters=distance_meters,
            calories=calories,
        )

    def list_activities(self, user_id: str, limit: int, offset: int):
        print(f"Controller(Activity): list_activities limit={limit} offset={offset}")
        return _call_with_supported_kwargs(self.repo.list_activities, user_id=user_id, limit=limit, offset=offset)


class GoalController:
    def __init__(self, repo: GoalRepository):
        self.repo = repo

    def create_goal(self, user_id: str, goal_type: str, target_value: int, period_start: str, period_end=None):
        print("Controller(Goal): create_goal")
        return _call_with_supported_kwargs(
            self.repo.create_goal,
            user_id=user_id,
            goal_type=goal_type,
            target_value=target_value,
            period_start=period_start,
            period_end=period_end,
        )


async def main():
    print("=== Group 11 Demo Script (MS3) ===")
    print("Flow: User -> Controller -> Repository -> Database")

    await db.connect()
    conn = db.get_connection()

    user_repo = UserRepository(conn)
    activity_repo = ActivityRepository(conn)
    goal_repo = GoalRepository(conn)

    user_ctrl = UserController(user_repo)
    activity_ctrl = ActivityController(activity_repo)
    goal_ctrl = GoalController(goal_repo)

    ts = int(time.time())
    email = f"demo_{ts}@example.com"
    uname = f"Demo User {ts}"

    print("\n1) CREATE USER")
    user = user_ctrl.create_user(email=email, name=uname)
    user_id = user["id"]
    print("Created user (repo return):", user)
    print("User id in DB:", user_id)

    print("\n2) UPSERT ACTIVITY (add 3 activities)")
    base = datetime.now(timezone.utc)
    a1 = activity_ctrl.upsert_activity(
        user_id=user_id,
        provider="demo",
        external_id=f"act_{ts}_1",
        name="Running",
        activity_type="Running",
        start_time=_utc_iso(base),
        duration_seconds=900,
        distance_meters=2500,
        calories=200,
    )
    print("Upserted activity 1:", a1)

    a2 = activity_ctrl.upsert_activity(
        user_id=user_id,
        provider="demo",
        external_id=f"act_{ts}_2",
        name="Reading",
        activity_type="Reading",
        start_time=_utc_iso(base.replace(minute=(base.minute - 5) % 60)),
        duration_seconds=1800,
        distance_meters=None,
        calories=None,
    )
    print("Upserted activity 2:", a2)

    a3 = activity_ctrl.upsert_activity(
        user_id=user_id,
        provider="demo",
        external_id=f"act_{ts}_3",
        name="Gym",
        activity_type="Gym",
        start_time=_utc_iso(base.replace(minute=(base.minute - 10) % 60)),
        duration_seconds=3600,
        distance_meters=None,
        calories=350,
    )
    print("Upserted activity 3:", a3)

    print("\n3) LIST ACTIVITIES WITH PAGINATION")
    page1 = activity_ctrl.list_activities(user_id=user_id, limit=2, offset=0)
    print("Page 1:", page1)
    page2 = activity_ctrl.list_activities(user_id=user_id, limit=2, offset=2)
    print("Page 2:", page2)

    print("\n4) CREATE GOAL")
    period_start = _utc_iso(datetime.now(timezone.utc))
    goal = goal_ctrl.create_goal(user_id=user_id, goal_type="steps", target_value=10000, period_start=period_start)
    print("Created goal:", goal)

    await db.disconnect()
    print("\n✅ Demo finished OK")


if __name__ == "__main__":
    asyncio.run(main())