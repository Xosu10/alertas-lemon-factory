import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = str(Path(__file__).parent / "events.db")


def init_db():
    """Crea la tabla de eventos ya avisados si no existe. Se puede llamar en cada arranque."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notified_events (
            event_id TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            notified_at TEXT NOT NULL,
            PRIMARY KEY (event_id, notification_type)
        )
        """
    )
    conn.commit()
    conn.close()


def build_event_id(event):
    """Identificador estable del evento (el feed no trae uno propio)."""
    return f"{event['country']}|{event['title']}|{event['date']}"


def is_notified(event_id, notification_type):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT 1 FROM notified_events WHERE event_id = ? AND notification_type = ?",
        (event_id, notification_type),
    ).fetchone()
    conn.close()
    return row is not None


def mark_notified(event_id, notification_type):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO notified_events (event_id, notification_type, notified_at) VALUES (?, ?, ?)",
        (event_id, notification_type, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
