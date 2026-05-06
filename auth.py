"""auth.py — username/password auth stored in the app's SQLite database."""
import hashlib
import sqlite3
from typing import Optional, Tuple
import pandas as pd

_ADMIN = "Mahri"
_ADMIN_HASH = hashlib.sha256("Revita#2025".encode()).hexdigest()


def _h(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def init_users(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=?", (_ADMIN,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users(username, password_hash, is_admin) VALUES(?,?,1)",
            (_ADMIN, _ADMIN_HASH),
        )
        conn.commit()


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> Optional[Tuple]:
    """Returns (id, username, is_admin) or None."""
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, is_admin FROM users WHERE username=? AND password_hash=?",
        (username, _h(password)),
    )
    return cur.fetchone()


def list_users(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql(
        "SELECT id, username, is_admin, created_at FROM users ORDER BY username", conn
    )


def add_user(conn: sqlite3.Connection, username: str, password: str, is_admin: bool) -> bool:
    try:
        conn.execute(
            "INSERT INTO users(username, password_hash, is_admin) VALUES(?,?,?)",
            (username, _h(password), int(is_admin)),
        )
        conn.commit()
        return True
    except Exception:
        return False


def delete_user(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("DELETE FROM users WHERE id=? AND username!=?", (user_id, _ADMIN))
    conn.commit()


def set_password(conn: sqlite3.Connection, user_id: int, new_password: str) -> None:
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (_h(new_password), user_id))
    conn.commit()
