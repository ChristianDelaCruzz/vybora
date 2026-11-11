"""SQLite connection helper."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from typing import Iterator
from config.settings import DATABASE_PATH

_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    """Get a valid database connection, reopening if it was closed."""
    global _connection

    # If the connection exists but is closed, reset it
    if _connection is not None:
        try:
            _connection.execute("SELECT 1")
        except sqlite3.ProgrammingError:
            # The connection was closed externally. Reset it.
            _connection = None
        except sqlite3.Error:
            _connection = None

    # Create a fresh connection if needed
    if _connection is None:
        _connection = sqlite3.connect(
            str(DATABASE_PATH),
            check_same_thread=False
        )
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON;")
    
    return _connection


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def close_connection() -> None:
    global _connection
    if _connection is not None:
        try:
            _connection.close()
        except Exception:
            pass
        _connection = None