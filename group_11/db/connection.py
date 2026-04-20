from __future__ import annotations

import sqlite3
from pathlib import Path


DB_FILE = Path(__file__).resolve().parent / "group11.sqlite3"
SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


class Database:
    def __init__(self) -> None:
        self._conn: sqlite3.Connection | None = None

    async def connect(self) -> None:
        if self._conn is None:
            self._conn = sqlite3.connect(DB_FILE)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON;")

            schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
            self._conn.executescript(schema_sql)
            self._conn.commit()

            print(f"SQLite DB connected: {DB_FILE}")

    async def disconnect(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            print("SQLite DB disconnected")

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database is not connected. Call await db.connect() first.")
        return self._conn


db = Database()