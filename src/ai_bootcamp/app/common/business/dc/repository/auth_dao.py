import sqlite3
from typing import Any, Dict, List, Optional


class AuthDAO:
    """인증 관련 데이터 접근 객체 (DAO)"""

    def __init__(self, db_path: str = "auth.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 사용자 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 세션 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """
            )

            # 기본 관리자 계정 생성
            cursor.execute(
                """
                INSERT OR IGNORE INTO users (username, password_hash)
                VALUES (?, ?)
            """,
                ("admin", "admin123"),
            )

            conn.commit()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """사용자명으로 사용자 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, username, password_hash, created_at, updated_at
                FROM users WHERE username = ?
            """,
                (username,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                }
            return None

    def create_session(
        self, session_id: str, username: str, expires_at: Optional[str] = None
    ) -> bool:
        """세션 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO sessions (session_id, username, expires_at)
                    VALUES (?, ?, ?)
                """,
                    (session_id, username, expires_at),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, session_id, username, created_at, expires_at, is_active
                FROM sessions WHERE session_id = ? AND is_active = 1
            """,
                (session_id,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "session_id": row[1],
                    "username": row[2],
                    "created_at": row[3],
                    "expires_at": row[4],
                    "is_active": bool(row[5]),
                }
            return None

    def deactivate_session(self, session_id: str) -> bool:
        """세션 비활성화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sessions SET is_active = 0
                WHERE session_id = ?
            """,
                (session_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """활성 세션 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, username, created_at
                FROM sessions WHERE is_active = 1
            """
            )

            return [
                {"session_id": row[0], "username": row[1], "created_at": row[2]}
                for row in cursor.fetchall()
            ]
