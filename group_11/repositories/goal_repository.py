import sqlite3
from typing import Dict, Optional
from uuid import uuid4


class GoalRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_goal(
        self,
        user_id: str,
        goal_type: str,
        target_value: int,
        period_start: str,
        period_end: Optional[str] = None,
    ) -> Dict:
        self._validate_inputs(user_id, goal_type, target_value, period_start)

        goal_id = str(uuid4())
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals (id, user_id, type, target_value, period_start, period_end)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (goal_id, user_id, goal_type, int(target_value), period_start, period_end),
        )
        self.conn.commit()
        return self.get_goal_by_id(goal_id)

    def get_goal_by_id(self, goal_id: str) -> Optional[Dict]:
        self._validate_non_empty_str(goal_id, "goal_id")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, type, target_value, period_start, period_end
            FROM goals
            WHERE id = ?
            """,
            (goal_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return dict(
            zip(
                ["id", "user_id", "type", "target_value", "period_start", "period_end"],
                row,
            )
        )

    # ---------- Validation ----------
    def _validate_non_empty_str(self, value: str, field: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")

    def _validate_inputs(self, user_id: str, goal_type: str, target_value: int, period_start: str) -> None:
        self._validate_non_empty_str(user_id, "user_id")
        self._validate_non_empty_str(goal_type, "goal_type")
        self._validate_non_empty_str(period_start, "period_start")

        if not isinstance(target_value, int):
            raise ValueError("target_value must be an int")
        if target_value <= 0:
            raise ValueError("target_value must be > 0")