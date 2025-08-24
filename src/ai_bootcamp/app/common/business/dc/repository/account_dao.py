import logging
import sqlite3
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AccountDAO:
    """Account 관련 데이터 접근 객체 (DAO)"""

    def __init__(self, db_path: str = "auth.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Account 테이블 초기화"""
        logger.info(
            f"IN: AccountDAO.init_database() - DB 초기화: db_path={self.db_path}"
        )
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Account 테이블 생성
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS account (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        company TEXT,
                        password TEXT NOT NULL,
                        juso TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # 기본 관리자 계정 생성 (admin/admin123)
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO account (id, name, company, password, juso)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    ("admin", "관리자", "AI Bootcamp", "admin123", "서울시 강남구"),
                )

                # 테스트 계정 추가
                test_accounts = [
                    ("user1", "홍길동", "테스트회사1", "password1", "서울시 서초구"),
                    ("user2", "김철수", "테스트회사2", "password2", "서울시 마포구"),
                    ("user3", "이영희", "테스트회사3", "password3", "서울시 종로구"),
                ]

                for account in test_accounts:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO account (id, name, company, password, juso)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        account,
                    )

                conn.commit()
            logger.info("OUT: AccountDAO.init_database() - DB 초기화 완료")
        except Exception as e:
            logger.error(f"OUT: AccountDAO.init_database() - DB 초기화 오류: {e}")
            raise

    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """ID로 계정 조회"""
        logger.info(
            f"IN: AccountDAO.get_account_by_id() - 계정 조회: account_id={account_id}"
        )
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, name, company, password, juso, created_at, updated_at
                    FROM account WHERE id = ?
                """,
                    (account_id,),
                )

                row = cursor.fetchone()
                if row:
                    result = {
                        "id": row[0],
                        "name": row[1],
                        "company": row[2],
                        "password": row[3],
                        "juso": row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                    }
                    logger.info(
                        f"OUT: AccountDAO.get_account_by_id() - 계정 조회 성공: account_id={account_id}"
                    )
                    return result
                logger.warning(
                    f"OUT: AccountDAO.get_account_by_id() - 계정 없음: account_id={account_id}"
                )
                return None
        except Exception as e:
            logger.error(
                f"OUT: AccountDAO.get_account_by_id() - 계정 조회 오류: account_id={account_id}, error={e}"
            )
            raise

    def validate_account(self, account_id: str, password: str) -> bool:
        """계정 인증 검증"""
        logger.info(
            f"IN: AccountDAO.validate_account() - 계정 인증: account_id={account_id}"
        )
        try:
            account = self.get_account_by_id(account_id)
            if account:
                result = account["password"] == password
                logger.info(
                    f"OUT: AccountDAO.validate_account() - 인증 결과: account_id={account_id}, success={result}"
                )
                return result
            logger.warning(
                f"OUT: AccountDAO.validate_account() - 계정 없음: account_id={account_id}"
            )
            return False
        except Exception as e:
            logger.error(
                f"OUT: AccountDAO.validate_account() - 인증 오류: account_id={account_id}, error={e}"
            )
            raise

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """모든 계정 조회 (비밀번호 제외)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, company, juso, created_at, updated_at
                FROM account ORDER BY created_at DESC
            """
            )

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "company": row[2],
                    "juso": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                }
                for row in cursor.fetchall()
            ]

    def create_account(
        self, account_id: str, name: str, company: str, password: str, juso: str
    ) -> bool:
        """새 계정 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO account (id, name, company, password, juso)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (account_id, name, company, password, juso),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def update_account(
        self,
        account_id: str,
        name: str = None,
        company: str = None,
        password: str = None,
        juso: str = None,
    ) -> bool:
        """계정 정보 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 업데이트할 필드들 구성
            update_fields = []
            params = []

            if name is not None:
                update_fields.append("name = ?")
                params.append(name)
            if company is not None:
                update_fields.append("company = ?")
                params.append(company)
            if password is not None:
                update_fields.append("password = ?")
                params.append(password)
            if juso is not None:
                update_fields.append("juso = ?")
                params.append(juso)

            if not update_fields:
                return False

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(account_id)

            query = f"UPDATE account SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

            return cursor.rowcount > 0

    def delete_account(self, account_id: str) -> bool:
        """계정 삭제"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM account WHERE id = ?", (account_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_account_count(self) -> int:
        """계정 수 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM account")
            return cursor.fetchone()[0]
