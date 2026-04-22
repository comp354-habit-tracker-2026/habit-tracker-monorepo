import sqlite3
from typing import List, Dict, Optional


class GoalRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_goal(self, user_id: int, title: str, target: int) -> Dict:
        self._validate_inputs(user_id, title, target)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals (user_id, title, target)
            VALUES (?, ?, ?)
            """,
            (user_id, title, target),
        )
        self.conn.commit()

        goal_id = cursor.lastrowid
        return self.get_goal_by_id(goal_id)

    def list_goals(self, user_id: int) -> List[Dict]:
        self._validate_id(user_id)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, user_id, title, target FROM goals WHERE user_id = ?",
            (user_id,),
        )

        rows = cursor.fetchall()

        return [
            dict(zip(["id", "user_id", "title", "target"], row))
            for row in rows
        ]

    def get_goal_by_id(self, goal_id: int) -> Optional[Dict]:
        self._validate_id(goal_id)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, user_id, title, target FROM goals WHERE id = ?",
            (goal_id,),
        )

        row = cursor.fetchone()
        return dict(zip(["id", "user_id", "title", "target"], row)) if row else None

    # ---------- Validation ----------
    def _validate_inputs(self, user_id, title, target):
        if not user_id or user_id <= 0:
            raise ValueError("Invalid user_id")
        if not title:
            raise ValueError("Title required")
        if target <= 0:
            raise ValueError("Target must be positive")

    def _validate_id(self, value: int):
        if not value or value <= 0:
            raise ValueError("Invalid ID")
