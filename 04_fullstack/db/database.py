import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class PADatabase:
    """SQLite database for PAAM session logs and analytics"""

    def __init__(self, db_path: str = "./storage/chat_logs.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    topic TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    time_limit_minutes INTEGER,
                    topics_covered TEXT,
                    questions_count INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time_ms INTEGER,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS confusion_flags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    concept TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    correct BOOLEAN NOT NULL,
                    attempts INTEGER DEFAULT 1,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_confusion_session 
                ON confusion_flags(session_id)
            """)

    def create_session(self, session_id: str, topic: str, time_limit: int) -> int:
        """Create a new session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, topic, time_limit_minutes)
                VALUES (?, ?, ?)
            """,
                (session_id, topic, time_limit),
            )
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def end_session(self, session_id: str, topics_covered: List[str]):
        """Mark session as completed"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE sessions 
                SET ended_at = CURRENT_TIMESTAMP,
                    completed = TRUE,
                    topics_covered = ?,
                    questions_count = (
                        SELECT COUNT(*) FROM messages 
                        WHERE session_id = ? AND role = 'user'
                    )
                WHERE session_id = ?
            """,
                (",".join(topics_covered), session_id, session_id),
            )

    def log_message(
        self, session_id: str, role: str, content: str, response_time_ms: int = None
    ):
        """Log a chat message"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO messages (session_id, role, content, response_time_ms)
                VALUES (?, ?, ?, ?)
            """,
                (session_id, role, content, response_time_ms),
            )

    def log_confusion(self, session_id: str, concept: str):
        """Log a confusion flag"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO confusion_flags (session_id, concept)
                VALUES (?, ?)
            """,
                (session_id, concept),
            )

    def get_unresolved_confusion(self) -> List[Dict[str, Any]]:
        """Get all unresolved confusion flags"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [
                dict(row)
                for row in conn.execute("""
                SELECT * FROM confusion_flags WHERE resolved = FALSE
            """).fetchall()
            ]

    def resolve_confusion(self, concept: str):
        """Mark confusion as resolved"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE confusion_flags 
                SET resolved = TRUE 
                WHERE concept = ?
            """,
                (concept,),
            )

    def log_quiz_result(
        self, session_id: str, question: str, correct: bool, attempts: int = 1
    ):
        """Log quiz result"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO quiz_results (session_id, question, correct, attempts)
                VALUES (?, ?, ?, ?)
            """,
                (session_id, question, correct, attempts),
            )

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            session = conn.execute(
                """
                SELECT * FROM sessions WHERE session_id = ?
            """,
                (session_id,),
            ).fetchone()

            messages = conn.execute(
                """
                SELECT COUNT(*) as count FROM messages WHERE session_id = ?
            """,
                (session_id,),
            ).fetchone()

            confusion = conn.execute(
                """
                SELECT COUNT(*) as count FROM confusion_flags 
                WHERE session_id = ? AND resolved = FALSE
            """,
                (session_id,),
            ).fetchone()

            return {
                "session": dict(session) if session else None,
                "message_count": messages["count"],
                "confusion_count": confusion["count"],
            }

    def get_all_confusion_concepts(self) -> List[str]:
        """Get all concepts that caused confusion"""
        with sqlite3.connect(self.db_path) as conn:
            return [
                row[0]
                for row in conn.execute("""
                SELECT DISTINCT concept FROM confusion_flags 
                WHERE resolved = FALSE
            """).fetchall()
            ]

    def get_quiz_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get quiz score trend over days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [
                dict(row)
                for row in conn.execute(
                    """
                SELECT DATE(timestamp) as date, 
                       AVG(CASE WHEN correct THEN 1.0 ELSE 0.0 END) as score
                FROM quiz_results
                WHERE timestamp >= DATE('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """,
                    (days,),
                ).fetchall()
            ]


db = PADatabase()
