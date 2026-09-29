import sqlite3
from typing import Optional, Dict
from backend.utils.security import get_password_hash, verify_password

DB_PATH = "backend/database/app.db"

CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(CREATE_USERS_SQL)
    conn.commit()
    conn.close()


def create_user(username: str, password: str) -> Dict:
    conn = _get_conn()
    cur = conn.cursor()
    pw_hash = get_password_hash(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        conn.commit()
        user_id = cur.lastrowid
    except Exception as e:
        conn.close()
        raise
    conn.close()
    return {"id": user_id, "username": username}


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "username": row["username"]}
