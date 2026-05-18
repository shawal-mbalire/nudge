from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.utils import normalize_energy

DB_FILE = Path.home() / ".nudge.db"
LEGACY_JSON_FILE = Path.home() / ".nudge.json"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            desc TEXT NOT NULL,
            project TEXT NOT NULL,
            energy TEXT NOT NULL CHECK (energy IN ('low', 'medium', 'high')),
            status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'done')),
            created_at TEXT NOT NULL
        )
        """
    )
    _migrate_legacy_json(conn)
    return conn


def _migrate_legacy_json(conn: sqlite3.Connection) -> None:
    if not LEGACY_JSON_FILE.exists():
        return

    task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if task_count > 0:
        return

    raw = LEGACY_JSON_FILE.read_text().strip()
    if not raw:
        return

    data = json.loads(raw)
    if not isinstance(data, dict) or "tasks" not in data:
        raise RuntimeError("~/.nudge.json is invalid. Could not migrate.")

    for task in data["tasks"]:
        conn.execute(
            """
            INSERT INTO tasks (id, desc, project, energy, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task["id"],
                task["desc"],
                task["project"],
                normalize_energy(task["energy"]),
                "done" if task["status"] == "done" else "open",
                task["created_at"],
            ),
        )
    conn.commit()


def create_task(desc: str, project: str, energy: str) -> sqlite3.Row:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (desc, project, energy, status, created_at)
            VALUES (?, ?, ?, 'open', ?)
            """,
            (
                desc,
                project,
                normalize_energy(energy),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        task_id = cursor.lastrowid
        return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def fetch_tasks(
    *,
    project: str | None = None,
    energy: str | None = None,
    include_done: bool = False,
) -> list[dict]:
    query = "SELECT id, desc, project, energy, status, created_at FROM tasks WHERE 1=1"
    params: list[str] = []

    if project:
        query += " AND project = ?"
        params.append(project)
    if energy:
        query += " AND energy = ?"
        params.append(normalize_energy(energy))
    if not include_done:
        query += " AND status = 'open'"

    query += " ORDER BY project ASC, id ASC"

    with connect() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()

    return [dict(row) for row in rows]


def fetch_task_by_id(task_id: int) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT id, desc, project, energy, status, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return dict(row) if row else None


def set_task_done(task_id: int) -> bool:
    with connect() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = 'done' WHERE id = ? AND status != 'done'",
            (task_id,),
        )
        conn.commit()
    return cursor.rowcount > 0
