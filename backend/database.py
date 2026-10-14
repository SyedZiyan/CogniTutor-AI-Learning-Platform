import os
import sqlite3
import json
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.config import DATA_DIR

DB_PATH = os.path.join(DATA_DIR, "cognitutor.db")

class DatabaseManager:
    """
    SQLite Relational Database Manager for CogniTutor.
    Provides persistent ACID storage for documents, chunks, quiz attempts,
    student profiles, chat transcripts, and Socratic viva defense sessions.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        """Initializes tables, indices, and constraints."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Documents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                file_size_kb REAL,
                chunk_count INTEGER DEFAULT 0,
                topics_json TEXT,
                is_sample INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Chunks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                text TEXT NOT NULL,
                topic TEXT,
                page_or_slide TEXT,
                section_or_title TEXT,
                exact_citation TEXT,
                bbox_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_topic ON chunks(topic);")

            # 3. Quiz Attempts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                selected_index INTEGER,
                is_correct INTEGER NOT NULL,
                difficulty TEXT,
                xp_earned INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_topic ON quiz_attempts(topic);")

            # 4. Student Profile table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                user_id TEXT PRIMARY KEY,
                name TEXT DEFAULT 'Scholar',
                xp INTEGER DEFAULT 820,
                level INTEGER DEFAULT 5,
                streak_days INTEGER DEFAULT 7,
                quizzes_completed INTEGER DEFAULT 24,
                badges_json TEXT,
                topic_mastery_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 5. Chat History table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT DEFAULT 'default',
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                citations_json TEXT,
                retrieval_strategy TEXT DEFAULT 'Hybrid-BM25-Dense-RRF',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);")

            # 6. Socratic Viva Defense History table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS viva_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                student_name TEXT,
                round_number INTEGER NOT NULL,
                examiner_question TEXT NOT NULL,
                student_defense TEXT NOT NULL,
                score INTEGER,
                critique TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_viva_session ON viva_history(session_id);")

            # 7. Roadmap Progress table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_progress (
                milestone_id TEXT PRIMARY KEY,
                completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()

    # --- Document & Chunk Methods ---

    def save_document(self, doc_meta: Dict[str, Any], chunks: List[Any]):
        """Persists document metadata and associated chunks."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            topics_json = json.dumps(doc_meta.get("topics", []))
            cursor.execute("""
            INSERT INTO documents (doc_id, file_name, file_path, file_type, file_size_kb, chunk_count, topics_json, is_sample)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(doc_id) DO UPDATE SET
                file_name = excluded.file_name,
                file_path = excluded.file_path,
                file_type = excluded.file_type,
                file_size_kb = excluded.file_size_kb,
                chunk_count = excluded.chunk_count,
                topics_json = excluded.topics_json,
                is_sample = excluded.is_sample;
            """, (
                doc_meta["doc_id"],
                doc_meta.get("file_name", ""),
                doc_meta.get("file_path", ""),
                doc_meta.get("file_type", ""),
                doc_meta.get("file_size_kb", 0.0),
                len(chunks),
                topics_json,
                1 if doc_meta.get("is_sample") else 0
            ))

            # Delete existing chunks for this document before inserting refreshed ones
            cursor.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_meta["doc_id"],))

            chunk_rows = []
            for c in chunks:
                c_dict = c.to_dict() if hasattr(c, "to_dict") else dict(c)
                chunk_rows.append((
                    c_dict.get("chunk_id", ""),
                    doc_meta["doc_id"],
                    c_dict.get("text", ""),
                    c_dict.get("topic", "General"),
                    str(c_dict.get("page_or_slide", "")),
                    c_dict.get("section_or_title", ""),
                    c_dict.get("exact_citation", ""),
                    json.dumps(c_dict.get("bbox", {}))
                ))

            cursor.executemany("""
            INSERT OR REPLACE INTO chunks (chunk_id, doc_id, text, topic, page_or_slide, section_or_title, exact_citation, bbox_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, chunk_rows)

            conn.commit()

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieves all indexed documents."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents ORDER BY is_sample DESC, file_name ASC")
            rows = cursor.fetchall()
            docs = []
            for r in rows:
                docs.append({
                    "doc_id": r["doc_id"],
                    "file_name": r["file_name"],
                    "file_path": r["file_path"],
                    "file_type": r["file_type"],
                    "file_size_kb": r["file_size_kb"],
                    "chunk_count": r["chunk_count"],
                    "topics": json.loads(r["topics_json"]) if r["topics_json"] else [],
                    "is_sample": bool(r["is_sample"]),
                    "created_at": r["created_at"]
                })
            return docs

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """Retrieves all chunks belonging to a document."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chunks WHERE doc_id = ? ORDER BY chunk_id ASC", (doc_id,))
            rows = cursor.fetchall()
            chunks = []
            for r in rows:
                chunks.append({
                    "chunk_id": r["chunk_id"],
                    "doc_id": r["doc_id"],
                    "text": r["text"],
                    "topic": r["topic"],
                    "page_or_slide": r["page_or_slide"],
                    "section_or_title": r["section_or_title"],
                    "exact_citation": r["exact_citation"],
                    "bbox": json.loads(r["bbox_json"]) if r["bbox_json"] else {}
                })
            return chunks

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieves all indexed chunks across all documents."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chunks ORDER BY doc_id, chunk_id")
            rows = cursor.fetchall()
            chunks = []
            for r in rows:
                chunks.append({
                    "chunk_id": r["chunk_id"],
                    "doc_id": r["doc_id"],
                    "text": r["text"],
                    "topic": r["topic"],
                    "page_or_slide": r["page_or_slide"],
                    "section_or_title": r["section_or_title"],
                    "exact_citation": r["exact_citation"],
                    "bbox": json.loads(r["bbox_json"]) if r["bbox_json"] else {}
                })
            return chunks

    # --- Quiz Attempts ---

    def record_quiz_attempt(self, question_id: str, topic: str, selected_index: int,
                            is_correct: bool, difficulty: str, xp_earned: int):
        with self._lock, self.get_connection() as conn:
            conn.execute("""
            INSERT INTO quiz_attempts (question_id, topic, selected_index, is_correct, difficulty, xp_earned)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (question_id, topic, selected_index, 1 if is_correct else 0, difficulty, xp_earned))
            conn.commit()

    def get_quiz_attempts(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quiz_attempts ORDER BY attempt_id DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    # --- Student Profile & Gamification ---

    def save_student_profile(self, user_id: str, name: str, xp: int, level: int,
                             streak_days: int, quizzes_completed: int,
                             badges: List[Dict[str, Any]], topic_mastery: Dict[str, Any]):
        with self._lock, self.get_connection() as conn:
            conn.execute("""
            INSERT INTO student_profile (user_id, name, xp, level, streak_days, quizzes_completed, badges_json, topic_mastery_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                xp = excluded.xp,
                level = excluded.level,
                streak_days = excluded.streak_days,
                quizzes_completed = excluded.quizzes_completed,
                badges_json = excluded.badges_json,
                topic_mastery_json = excluded.topic_mastery_json,
                updated_at = CURRENT_TIMESTAMP;
            """, (
                user_id, name, xp, level, streak_days, quizzes_completed,
                json.dumps(badges), json.dumps(topic_mastery)
            ))
            conn.commit()

    def get_student_profile(self, user_id: str = "default_student") -> Optional[Dict[str, Any]]:
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_profile WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "xp": row["xp"],
                "level": row["level"],
                "streak_days": row["streak_days"],
                "quizzes_completed": row["quizzes_completed"],
                "badges": json.loads(row["badges_json"]) if row["badges_json"] else [],
                "topic_mastery": json.loads(row["topic_mastery_json"]) if row["topic_mastery_json"] else {},
                "updated_at": row["updated_at"]
            }

    # --- Chat Interactions ---

    def record_chat(self, query: str, answer: str, citations: List[Any],
                    retrieval_strategy: str = "Hybrid-BM25-Dense-RRF", session_id: str = "default"):
        with self._lock, self.get_connection() as conn:
            conn.execute("""
            INSERT INTO chat_history (session_id, query, answer, citations_json, retrieval_strategy)
            VALUES (?, ?, ?, ?, ?)
            """, (
                session_id, query, answer,
                json.dumps(citations),
                retrieval_strategy
            ))
            conn.commit()

    def get_recent_chat(self, session_id: str = "default", limit: int = 30) -> List[Dict[str, Any]]:
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM chat_history WHERE session_id = ? ORDER BY message_id DESC LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            chats = []
            for r in rows:
                chats.append({
                    "message_id": r["message_id"],
                    "session_id": r["session_id"],
                    "query": r["query"],
                    "answer": r["answer"],
                    "citations": json.loads(r["citations_json"]) if r["citations_json"] else [],
                    "retrieval_strategy": r["retrieval_strategy"],
                    "timestamp": r["timestamp"]
                })
            return chats

    # --- Viva Sessions ---

    def record_viva_defense(self, session_id: str, topic: str, student_name: str,
                            round_number: int, examiner_question: str,
                            student_defense: str, score: int, critique: str):
        with self._lock, self.get_connection() as conn:
            conn.execute("""
            INSERT INTO viva_history (session_id, topic, student_name, round_number, examiner_question, student_defense, score, critique)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, topic, student_name, round_number,
                examiner_question, student_defense, score, critique
            ))
            conn.commit()

    def get_viva_history(self, session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute("""
                SELECT * FROM viva_history WHERE session_id = ? ORDER BY round_number ASC
                """, (session_id,))
            else:
                cursor.execute("""
                SELECT * FROM viva_history ORDER BY id DESC LIMIT ?
                """, (limit,))
            return [dict(r) for r in cursor.fetchall()]

    # --- Database Statistics ---

    def get_db_stats(self) -> Dict[str, Any]:
        """Returns live statistics about database size and record counts."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM quiz_attempts")
            quiz_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM chat_history")
            chat_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM viva_history")
            viva_count = cursor.fetchone()[0]

            size_bytes = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

            return {
                "database_engine": "SQLite 3 (WAL Mode + Relational Integrity)",
                "database_file": os.path.abspath(self.db_path),
                "database_size_kb": round(size_bytes / 1024, 2),
                "total_documents": doc_count,
                "total_chunks": chunk_count,
                "total_quiz_attempts": quiz_count,
                "total_chat_interactions": chat_count,
                "total_viva_rounds": viva_count,
                "status": "connected"
            }

db = DatabaseManager()
