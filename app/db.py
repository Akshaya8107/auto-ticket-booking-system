import sqlite3
from pathlib import Path
from .config import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent

def _db_path() -> Path:
    url = get_settings().database_url
    prefix = "sqlite:///"
    if url.startswith(prefix):
        raw = url[len(prefix):]
        path = Path(raw)
        return path if path.is_absolute() else BASE_DIR / path
    raise RuntimeError("This local project expects a sqlite:/// DATABASE_URL")

def get_conn() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE NOT NULL,
            caller_name TEXT NOT NULL,
            caller_email TEXT NOT NULL,
            category TEXT,
            subcategory TEXT,
            short_description TEXT NOT NULL,
            description TEXT DEFAULT '',
            state TEXT NOT NULL DEFAULT 'New',
            assigned_group TEXT,
            assigned_to TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS flow_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            flow_name TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        );
        """)
