import sqlite3
from typing import List, Dict, Optional


class ActivityRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_activity_by_source(
        self,
        user_id: int,
        provider: str,
        external_id: str,
        name: str,
    ) -> Dict:
        self._validate_inputs(user_id, provider, external_id)

        cursor = self.conn.cursor()

        # Check for existing activity (deduplication)
        cursor.execute(
            """
            SELECT id FROM activities
            WHERE provider = ? AND external_id = ?
            """,
            (provider, external_id),
        )
        existing = cursor.fetchone()

        if existing:
            activity_id = existing[0]

            cursor.execute(
                """
                UPDATE activities
                SET name = ?, user_id = ?
                WHERE id = ?
                """,
                (name, user_id, activity_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO activities (user_id, provider, external_id, name)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, provider, external_id, name),
            )
            activity_id = cursor.lastrowid

        self.conn.commit()

        return self.get_activity_by_id(activity_id)

    def list_activities(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:
        self._validate_id(user_id)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, provider, external_id, name
            FROM activities
            WHERE user_id = ?
            LIMIT ? OFFSET ?
            """,
            (user_id, limit, offset),
        )

        rows = cursor.fetchall()

        return [
            dict(zip(["id", "user_id", "provider", "external_id", "name"], row))
            for row in rows
        ]

    def get_activity_by_id(self, activity_id: int) -> Optional[Dict]:
        self._validate_id(activity_id)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, provider, external_id, name
            FROM activities
            WHERE id = ?
            """,
            (activity_id,),
        )

        row = cursor.fetchone()
        return dict(zip(["id", "user_id", "provider", "external_id", "name"], row)) if row else None

    # ---------- Validation ----------
    def _validate_inputs(self, user_id, provider, external_id):
        if not user_id or user_id <= 0:
            raise ValueError("Invalid user_id")
        if not provider:
            raise ValueError("Provider required")
        if not external_id:
            raise ValueError("External ID required")

    def _validate_id(self, value: int):
        if not value or value <= 0:
            raise ValueError("Invalid ID")
