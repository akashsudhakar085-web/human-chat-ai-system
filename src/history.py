"""
============================================================
history.py  –  Chat History Manager (SQLite)
============================================================
Stores every conversation exchange in a local SQLite
database for persistence and review.

Each record stores:
  • user message
  • bot response
  • timestamp
  • detected sentiment
============================================================
"""

import os
import sqlite3
from datetime import datetime

# ── Database path ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "chat_history.db")


def _get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row        # access columns by name
    return conn


def init_db():
    """
    Create the chat_history table if it doesn't exist.
    Called once at application start.
    """
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_msg  TEXT    NOT NULL,
            bot_msg   TEXT    NOT NULL,
            sentiment TEXT    DEFAULT 'neutral',
            timestamp TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_chat(user_msg: str, bot_msg: str, sentiment: str = "neutral"):
    """
    Insert a single chat exchange into the database.

    Parameters
    ----------
    user_msg  : The user's original message.
    bot_msg   : The bot's response.
    sentiment : Detected sentiment label ('positive', 'negative', 'neutral').
    """
    conn = _get_connection()
    conn.execute(
        "INSERT INTO chat_history (user_msg, bot_msg, sentiment, timestamp) "
        "VALUES (?, ?, ?, ?)",
        (user_msg, bot_msg, sentiment, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_recent_chats(limit: int = 50) -> list:
    """
    Retrieve the most recent chat entries.

    Returns a list of dicts with keys:
        id, user_msg, bot_msg, sentiment, timestamp
    """
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows[::-1]           # reverse so oldest first


def clear_history():
    """Delete all chat history records."""
    conn = _get_connection()
    conn.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()


# ── Auto-create table on first import ─────────────────────
init_db()
