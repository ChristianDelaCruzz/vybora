"""Database queries for the Admin Dashboard and Management pages."""
import sqlite3
from database import connection as db_conn

def _get_conn():
    """Safely gets a database connection regardless of the function name."""
    if hasattr(db_conn, "connect"):
        return db_conn.connect()
    if hasattr(db_conn, "get_connection"):
        return db_conn.get_connection()
    if hasattr(db_conn, "get_db"):
        return db_conn.get_db()
    
    # Fallback to standard sqlite3 if needed
    import os
    db_path = os.path.join("data", "vybora.db")
    return sqlite3.connect(db_path)

def get_dashboard_stats() -> dict:
    stats = {"users": 0, "movies": 0, "games": 0, "music": 0}
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        for key, table in [("users", "users"), ("movies", "movies"), ("games", "games"), ("music", "music")]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[key] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                pass # Table doesn't exist yet
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
    return stats

def get_recent_activity(limit: int = 5) -> list[tuple]:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT action, created_at FROM activity_logs ORDER BY created_at DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_all_movies() -> list[tuple]:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT movie_id, title, release_date, rating FROM movies")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_all_users() -> list[tuple]:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role, created_at FROM users")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_all_games() -> list[tuple]:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        # Adjust columns if your games table is different
        cursor.execute("SELECT game_id, title, genre, platform, rating FROM games")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_all_logs() -> list[tuple]:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT created_at, action, description FROM activity_logs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []