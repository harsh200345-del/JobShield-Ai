"""
JobShield AI - SQLite Database Layer
Stores assessment history, risk reports, campus analytics, and student feedback.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import Config

DB_PATH = Config.DATABASE_PATH


def get_db_connection():
    """Returns a SQLite connection with dict-like row factories."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            document_name TEXT NOT NULL,
            input_type TEXT NOT NULL,
            company TEXT,
            role TEXT,
            stipend TEXT,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            critical_count INTEGER DEFAULT 0,
            warning_count INTEGER DEFAULT 0,
            analysis_json TEXT NOT NULL,
            summary TEXT,
            feedback_rating INTEGER DEFAULT 0,
            feedback_comments TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campus_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            details TEXT NOT NULL,
            reported_by TEXT DEFAULT 'Student / Placement Cell'
        )
    """)

    conn.commit()
    conn.close()


def save_scan(document_name: str, input_type: str, analysis: Dict[str, Any]) -> int:
    """Inserts a new scan report into the database and returns its row ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ext = analysis.get("extracted_data", {})
    counts = analysis.get("flags_count", {})

    cursor.execute("""
        INSERT INTO scans (
            timestamp, document_name, input_type, company, role, stipend,
            risk_score, risk_level, critical_count, warning_count,
            analysis_json, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        document_name,
        input_type,
        ext.get("company", "Unspecified"),
        ext.get("role", "Unspecified"),
        ext.get("stipend", "Unspecified"),
        analysis.get("risk_score", 0),
        analysis.get("risk_level", "LOW"),
        counts.get("critical", 0),
        counts.get("warning", 0),
        json.dumps(analysis),
        analysis.get("summary", "")
    ))

    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def get_scan(scan_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single scan record with its full parsed analysis object."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    data = dict(row)
    data["analysis"] = json.loads(data["analysis_json"])
    return data


def get_recent_scans(limit: int = 25) -> List[Dict[str, Any]]:
    """Retrieves latest scanned offers for history and placement cell oversight."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, document_name, input_type, company, role, stipend,
               risk_score, risk_level, critical_count, warning_count, summary
        FROM scans
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def get_analytics_summary() -> Dict[str, Any]:
    """Computes aggregate recruitment safety metrics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE risk_level = 'HIGH'")
    high_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE risk_level = 'MEDIUM'")
    medium_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE risk_level = 'LOW'")
    low_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(risk_score) FROM scans")
    avg_score_raw = cursor.fetchone()[0]
    avg_score = round(avg_score_raw, 1) if avg_score_raw else 0

    conn.close()

    return {
        "total_scans": total_scans,
        "high_risk": high_count,
        "medium_risk": medium_count,
        "low_risk": low_count,
        "avg_risk_score": avg_score,
        "high_risk_pct": round((high_count / total_scans * 100), 1) if total_scans > 0 else 0
    }


def save_feedback(scan_id: int, rating: int, comments: str):
    """Saves user/student feedback on a particular analysis."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE scans
        SET feedback_rating = ?, feedback_comments = ?
        WHERE id = ?
    """, (rating, comments, scan_id))
    conn.commit()
    conn.close()
