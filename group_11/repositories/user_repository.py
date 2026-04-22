import sqlite3
from typing import Optional, Dict


class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_user(self, email: str, name: str) -> Dict:
        self._validate_email(email)
        self._validate_name(name)

        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO users (email, name) VALUES (?, ?)",
            (email, name),
        )
        self.conn.commit()

        user_id = cursor.lastrowid

        return {"id": user_id, "email": email, "name": name}

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        self._validate_id(user_id)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, email, name FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        return dict(zip(["id", "email", "name"], row)) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        self._validate_email(email)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, email, name FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()

        return dict(zip(["id", "email", "name"], row)) if row else None

    # ---------- Validation ----------
    def _validate_email(self, email: str):
        if not email or "@" not in email:
            raise ValueError("Invalid email")

    def _validate_name(self, name: str):
        if not name:
            raise ValueError("Name cannot be empty")

    def _validate_id(self, value: int):
        if not value or value <= 0:
            raise ValueError("Invalid ID")
