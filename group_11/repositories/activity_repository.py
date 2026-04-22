import sqlite3
import uuid
from typing import List, Dict, Optional, Any


class ActivityRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # -------------------------
    # Public API
    # -------------------------
    def upsert_activity_by_source(
        self,
        user_id: Any,
        provider: str,
        external_id: str,
        name: str,
        activity_type: str,
        start_time: str,
        duration_seconds: int,
        distance_meters: Optional[int] = None,
        calories: Optional[int] = None,
    ) -> Dict:
        self._validate_user_id(user_id)
        self._validate_inputs(provider, external_id, name, activity_type, start_time, duration_seconds)

        # Make FK failure clearer (instead of sqlite generic error)
        if not self._user_exists(user_id):
            raise ValueError(f"user_id not found in users table: {user_id}")

        cur = self.conn.cursor()

        # Dedup by (provider, external_id)
        cur.execute(
            """
            SELECT id FROM activities
            WHERE provider = ? AND external_id = ?
            """,
            (provider, external_id),
        )
        row = cur.fetchone()

        if row:
            activity_id = row[0]
            cur.execute(
                """
                UPDATE activities
                SET
                    user_id = ?,
                    name = ?,
                    type = ?,
                    start_time = ?,
                    duration_seconds = ?,
                    distance_meters = ?,
                    calories = ?
                WHERE id = ?
                """,
                (
                    user_id,
                    name,
                    activity_type,
                    start_time,
                    int(duration_seconds),
                    distance_meters,
                    calories,
                    activity_id,
                ),
            )
        else:
            activity_id = self._new_activity_id()
            cur.execute(
                """
                INSERT INTO activities
                    (id, user_id, provider, external_id, name, type, start_time, duration_seconds, distance_meters, calories)
                VALUES
                    (?,  ?,      ?,        ?,          ?,    ?,    ?,          ?,                ?,               ?)
                """,
                (
                    activity_id,
                    user_id,
                    provider,
                    external_id,
                    name,
                    activity_type,
                    start_time,
                    int(duration_seconds),
                    distance_meters,
                    calories,
                ),
            )

        self.conn.commit()
        return self.get_activity_by_id(activity_id)

    def list_activities(self, user_id: Any, limit: int = 10, offset: int = 0) -> List[Dict]:
        self._validate_user_id(user_id)
        if limit <= 0:
            raise ValueError("limit must be > 0")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, provider, external_id, name, type, start_time, duration_seconds, distance_meters, calories
            FROM activities
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT ? OFFSET ?
            """,
            (user_id, int(limit), int(offset)),
        )
        rows = cur.fetchall()

        keys = ["id", "user_id", "provider", "external_id", "name", "type", "start_time", "duration_seconds", "distance_meters", "calories"]
        return [dict(zip(keys, r)) for r in rows]

    def get_activity_by_id(self, activity_id: Any) -> Optional[Dict]:
        self._validate_activity_id(activity_id)

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, provider, external_id, name, type, start_time, duration_seconds, distance_meters, calories
            FROM activities
            WHERE id = ?
            """,
            (activity_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        keys = ["id", "user_id", "provider", "external_id", "name", "type", "start_time", "duration_seconds", "distance_meters", "calories"]
        return dict(zip(keys, row))

    # -------------------------
    # Helpers / validation
    # -------------------------
    def _new_activity_id(self) -> str:
        # activities.id in your DB is effectively text UUID
        return str(uuid.uuid4())

    def _user_exists(self, user_id: Any) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (user_id,))
        return cur.fetchone() is not None

    def _validate_user_id(self, user_id: Any) -> None:
        # IMPORTANT: user_id can be UUID string (TEXT PK)
        if user_id is None:
            raise ValueError("user_id required")
        if isinstance(user_id, str):
            if user_id.strip() == "":
                raise ValueError("user_id required")
            return
        # allow int PK too (just in case)
        if isinstance(user_id, int):
            if user_id <= 0:
                raise ValueError("Invalid user_id")
            return
        raise ValueError("Invalid user_id type")

    def _validate_activity_id(self, activity_id: Any) -> None:
        if activity_id is None:
            raise ValueError("activity_id required")
        if isinstance(activity_id, str):
            if activity_id.strip() == "":
                raise ValueError("activity_id required")
            return
        if isinstance(activity_id, int):
            if activity_id <= 0:
                raise ValueError("Invalid activity_id")
            return
        raise ValueError("Invalid activity_id type")

    def _validate_inputs(
        self,
        provider: str,
        external_id: str,
        name: str,
        activity_type: str,
        start_time: str,
        duration_seconds: int,
    ) -> None:
        if not provider:
            raise ValueError("provider required")
        if not external_id:
            raise ValueError("external_id required")
        if not name:
            raise ValueError("name required")
        if not activity_type:
            raise ValueError("activity_type required")
        if not start_time:
            raise ValueError("start_time required")
        if duration_seconds is None:
            raise ValueError("duration_seconds required")
        if int(duration_seconds) < 0:
            raise ValueError("duration_seconds must be >= 0")