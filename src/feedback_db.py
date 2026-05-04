"""Feedback database schema and helpers."""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "feedback_log.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            message_id TEXT NOT NULL,
            user_input TEXT NOT NULL,
            agent_response TEXT NOT NULL,
            feedback_score INTEGER NOT NULL,
            optional_comment TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_feedback(thread_id: str, message_id: str, user_input: str,
                 agent_response: str, feedback_score: int, optional_comment: str = ""):
    conn = get_conn()
    conn.execute("""
        INSERT INTO feedback
            (timestamp, thread_id, message_id, user_input, agent_response, feedback_score, optional_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), thread_id, message_id,
          user_input, agent_response, feedback_score, optional_comment))
    conn.commit()
    conn.close()


def get_all_feedback():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM feedback ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_negative_feedback():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM feedback WHERE feedback_score = -1 ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
