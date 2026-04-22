import sqlite3
import uuid
from typing import Dict, Optional


class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _users_id_is_text(self) -> bool:
        # Detect if users.id is TEXT or INTEGER
        rows = self.conn.execute("PRAGMA table_info(users);").fetchall()
        # row format: (cid, name, type, notnull, dflt_value, pk)
        for r in rows:
            if r[1] == "id":
                col_type = (r[2] or "").upper()
                return "TEXT" in col_type or "CHAR" in col_type
        # default safe: treat as TEXT
        return True

    def create_user(self, email: str, name: str) -> Dict:
        if not email:
            raise ValueError("email required")
        if not name:
            raise ValueError("name required")

        cur = self.conn.cursor()

        id_is_text = self._users_id_is_text()

        if id_is_text:
            user_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO users (id, name, email)
                VALUES (?, ?, ?)
                """,
                (user_id, name, email),
            )
        else:
            # INTEGER PK schema
            cur.execute(
                """
                INSERT INTO users (name, email)
                VALUES (?, ?)
                """,
                (name, email),
            )
            user_id = cur.lastrowid

        self.conn.commit()

        return {"id": user_id, "email": email, "name": name}

    def get_user_by_id(self, user_id) -> Optional[Dict]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "email": row[2]}

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "email": row[2]}