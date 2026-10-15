"""SQLite connection and schema for the booking service."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS class_slot (
    id INTEGER PRIMARY KEY,
    site TEXT NOT NULL,
    starts_at TEXT NOT NULL,      -- ISO 8601, UTC
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);
"""


def connect(path=":memory:"):
    conn = sqlite3.connect(path, isolation_level=None)  # autocommit; use explicit BEGIN
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_slot(conn, site, starts_at, capacity):
    cur = conn.execute(
        "INSERT INTO class_slot (site, starts_at, capacity) VALUES (?, ?, ?)",
        (site, starts_at, capacity),
    )
    return cur.lastrowid
