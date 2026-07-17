"""
database.py
Very small SQLite layer used to keep a history of past resume scans so
the dashboard page can show trends over time.
"""

import json
import os
import sqlite3
from datetime import datetime

from config import Config


def get_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            job_title TEXT,
            domain TEXT,
            overall_score INTEGER NOT NULL,
            details_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_scan(filename: str, job_title: str, analysis: dict) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO scans (filename, job_title, domain, overall_score, details_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            job_title or "",
            analysis.get("domain", ""),
            analysis.get("overall_score", 0),
            json.dumps(analysis),
            datetime.utcnow().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_history(limit: int = 25):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, filename, job_title, domain, overall_score, created_at FROM scans ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_scan_by_id(scan_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["details"] = json.loads(result["details_json"])
    return result
