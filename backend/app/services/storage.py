"""
Lightweight in-memory + SQLite persistence for analysis results.

Modular design: swap the repository implementation later for PostgreSQL
without changing route handlers.
"""

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.config import settings

_lock = threading.Lock()


def _db_path() -> Path:
    # database_url like sqlite:///C:/path/analyses.db
    url = settings.database_url
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", "", 1))
    return Path(__file__).resolve().parent.parent / "data" / "analyses.db"


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    with _lock:
        conn = _connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    file_id TEXT,
                    filename TEXT,
                    created_at TEXT,
                    payload TEXT
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


def save_analysis(file_id: str, filename: str, payload: dict[str, Any]) -> str:
    """Persist analysis JSON and return analysis_id."""
    analysis_id = str(uuid.uuid4())
    created = datetime.now(timezone.utc).isoformat()
    # Convert pydantic models inside payload to plain JSON-serializable data
    serializable = _to_plain(payload)
    with _lock:
        conn = _connect()
        try:
            conn.execute(
                "INSERT INTO analyses (id, file_id, filename, created_at, payload) VALUES (?, ?, ?, ?, ?)",
                (analysis_id, file_id, filename, created, json.dumps(serializable)),
            )
            conn.commit()
        finally:
            conn.close()
    return analysis_id


def get_analysis(analysis_id: str) -> Optional[dict[str, Any]]:
    with _lock:
        conn = _connect()
        try:
            row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
            if not row:
                return None
            data = json.loads(row["payload"])
            data["analysis_id"] = row["id"]
            data["filename"] = row["filename"]
            data["file_id"] = row["file_id"]
            data["created_at"] = row["created_at"]
            return data
        finally:
            conn.close()


def _to_plain(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, list):
        return [_to_plain(v) for v in obj]
    return obj
