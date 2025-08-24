import logging
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AuthDC:
    """인증 관련 도메인 컴포넌트 (비즈니스 로직)"""

    def __init__(self):
        # 메모리 기반 세션 관리
        self.active_sessions = set()

    def process_authentication(self, username: str, password: str, account_dao) -> bool:
        """사용자 인증 처리 (비즈니스 로직) - Account 테이블 사용"""
        logger.info(
            f"IN: AuthDC.process_authentication() - 인증 처리: username={username}"
        )
        try:
            result = account_dao.validate_account(username, password)
            logger.info(
                f"OUT: AuthDC.process_authentication() - 인증 결과: username={username}, success={result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"OUT: AuthDC.process_authentication() - 인증 오류: username={username}, error={e}"
            )
            raise

    def create_session(self, username: str) -> str:
        """세션 생성 (비즈니스 로직)"""
        logger.info(f"IN: AuthDC.create_session() - 세션 생성: username={username}")
        try:
            session_id = f"session_{len(self.active_sessions) + 1}_{username}"
            self.active_sessions.add(session_id)
            logger.info(
                f"OUT: AuthDC.create_session() - 세션 생성 완료: username={username}, session_id={session_id}"
            )
            return session_id
        except Exception as e:
            logger.error(
                f"OUT: AuthDC.create_session() - 세션 생성 오류: username={username}, error={e}"
            )
            raise

    def validate_session(self, session_id: str) -> bool:
        """세션 유효성 검증 (비즈니스 로직)"""
        logger.info(
            f"IN: AuthDC.validate_session() - 세션 검증: session_id={session_id}"
        )
        try:
            result = session_id in self.active_sessions
            logger.info(
                f"OUT: AuthDC.validate_session() - 세션 검증 결과: session_id={session_id}, valid={result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"OUT: AuthDC.validate_session() - 세션 검증 오류: session_id={session_id}, error={e}"
            )
            raise

    def remove_session(self, session_id: str) -> bool:
        """세션 제거 (비즈니스 로직)"""
        logger.info(f"IN: AuthDC.remove_session() - 세션 제거: session_id={session_id}")
        try:
            if session_id in self.active_sessions:
                self.active_sessions.remove(session_id)
                logger.info(
                    f"OUT: AuthDC.remove_session() - 세션 제거 완료: session_id={session_id}"
                )
                return True
            logger.warning(
                f"OUT: AuthDC.remove_session() - 세션 없음: session_id={session_id}"
            )
            return False
        except Exception as e:
            logger.error(
                f"OUT: AuthDC.remove_session() - 세션 제거 오류: session_id={session_id}, error={e}"
            )
            raise

    def get_admin_config(self) -> Dict[str, Any]:
        """관리자 설정 정보 조회 (비즈니스 로직)"""
        logger.info("IN: AuthDC.get_admin_config() - 관리자 설정 조회")
        try:
            response = {
                "session_count": len(self.active_sessions),
                "active_sessions": list(self.active_sessions),
            }
            logger.info(
                f"OUT: AuthDC.get_admin_config() - 관리자 설정 조회 완료: session_count={len(self.active_sessions)}"
            )
            return response
        except Exception as e:
            logger.error(f"OUT: AuthDC.get_admin_config() - 관리자 설정 조회 오류: {e}")
            raise
