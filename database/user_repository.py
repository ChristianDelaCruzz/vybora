"""User database operations (Authentication, Registration, Profile, Settings, Stats)."""
import sqlite3
import hashlib
import os
import shutil
from pathlib import Path

from database.connection import get_connection
from config.settings import PROJECT_ROOT

class UserExistsError(Exception):
    pass

def _hash_password(password: str, salt: str) -> str:
    try:
        salt_bytes = bytes.fromhex(salt)
    except (ValueError, TypeError):
        salt_bytes = str(salt).encode('utf-8')

    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt_bytes, 
        100000
    ).hex()

def create_user(username: str, email: str, password: str, role: str = "User") -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        raise UserExistsError("Username or email already exists.")

    salt = os.urandom(16).hex()
    pwd_hash = _hash_password(password, salt)

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, salt, role) VALUES (?, ?, ?, ?, ?)",
            (username, email, pwd_hash, salt, role)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Database error during registration: {e}")
        return False

def authenticate_user(identifier: str, password: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT user_id, username, password_hash, salt, role FROM users WHERE username = ? OR email = ?",
        (identifier, identifier)
    )
    row = cursor.fetchone()

    if row:
        user_id, username, stored_hash, salt, role = row["user_id"], row["username"], row["password_hash"], row["salt"], row["role"]
        calculated_hash = _hash_password(password, salt)
        if calculated_hash == stored_hash:
            return {"user_id": user_id, "username": username, "role": role}
    
    return None

def get_user_profile(username: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email, role, created_at FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if row:
        return {
            "user_id": row["user_id"],
            "username": row["username"], 
            "email": row["email"], 
            "role": row["role"], 
            "created_at": row["created_at"]
        }
    return {}

def update_user_profile(old_username: str, new_username: str, new_email: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET username = ?, email = ? WHERE username = ?", 
            (new_username, new_email, old_username)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating profile: {e}")
        return False

def change_user_password(username: str, current_pw: str, new_pw: str) -> bool:
    user = authenticate_user(username, current_pw)
    if not user:
        return False
        
    salt = os.urandom(16).hex()
    new_hash = _hash_password(new_pw, salt)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", 
            (new_hash, salt, username)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error changing password: {e}")
        return False

# ==========================================
# SETTINGS FUNCTIONS
# ==========================================
def get_settings(user_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)", (user_id,))
    conn.commit()
    cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else {}

def save_setting(user_id: int, setting_name: str, value) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE user_settings SET {setting_name} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving setting: {e}")
        return False

# ==========================================
# STATS & HISTORY FUNCTIONS
# ==========================================
def get_user_stats(user_id: int) -> dict:
    """Fetch real entertainment statistics for the user."""
    stats = {"movies": 0, "tv": 0, "games": 0, "videos": 0, "music": 0, "total_time": 0}
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM media_history WHERE user_id = ? AND media_type = 'movie'", (user_id,))
        stats["movies"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM media_history WHERE user_id = ? AND media_type = 'tv'", (user_id,))
        stats["tv"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM media_history WHERE user_id = ? AND media_type = 'game'", (user_id,))
        stats["games"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM media_history WHERE user_id = ? AND media_type = 'video'", (user_id,))
        stats["videos"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM media_history WHERE user_id = ? AND media_type = 'music'", (user_id,))
        stats["music"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(duration) FROM media_history WHERE user_id = ?", (user_id,))
        total_seconds = cursor.fetchone()[0] or 0
        stats["total_time"] = total_seconds // 60
    except Exception as e:
        print(f"Error fetching stats: {e}")
        
    conn.close()
    return stats

def get_recent_activity(user_id: int, limit: int = 10) -> list[dict]:
    """Fetch the most recent history items for the user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT media_type, tmdb_id, title, poster_path, watched_at, duration
            FROM media_history 
            WHERE user_id = ? 
            ORDER BY watched_at DESC 
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching history: {e}")
        conn.close()
        return []

# ==========================================
# DANGER ZONE ACTIONS
# ==========================================
def clear_user_history(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM media_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM media_favorites WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        return False

def reset_user_settings(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO user_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error resetting settings: {e}")
        return False

def delete_user_account(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM media_favorites WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM media_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting account: {e}")
        return False

def clear_cache_files() -> str:
    cache_dir = PROJECT_ROOT / "cache"
    if not cache_dir.exists():
        return "0.0 MB"

    total_size = 0
    for f in cache_dir.rglob("*"):
        if f.is_file():
            total_size += f.stat().st_size

    try:
        shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        mb = total_size / (1024 * 1024)
        return f"{mb:.1f} MB"
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return "0.0 MB"