import logging
from typing import Optional

from fastapi import HTTPException

from ...transfer.auth_dto import (LoginRequestDto, LoginResponseDto,
                                  LogoutResponseDto)
from ..dc.auth_dc import AuthDC
from ..dc.repository.account_dao import AccountDAO
from ..dc.repository.auth_dao import AuthDAO

logger = logging.getLogger(__name__)


class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self):
        self.auth_dc = AuthDC()
        self.auth_dao = AuthDAO()
        self.account_dao = AccountDAO()

    def login(self, request: LoginRequestDto) -> LoginResponseDto:
        """로그인 처리"""
        logger.info(
            f"IN: AuthService.login() - 로그인 요청: username={request.username}"
        )

        try:
            # 인증 정보 검증 (Account 테이블 사용)
            logger.info(
                f"AuthService.login() - 인증 정보 검증 시작: username={request.username}"
            )
            if not self.auth_dc.process_authentication(
                request.username, request.password, self.account_dao
            ):
                logger.warning(
                    f"AuthService.login() - 인증 실패: username={request.username}"
                )
                raise HTTPException(
                    status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다."
                )

            # 세션 생성
            logger.info(
                f"AuthService.login() - 세션 생성 시작: username={request.username}"
            )
            session_id = self.auth_dc.create_session(request.username)
            # DB에 세션 저장
            self.auth_dao.create_session(session_id, request.username)

            response = LoginResponseDto(
                message="로그인 성공", success=True, token=session_id
            )
            logger.info(
                f"OUT: AuthService.login() - 로그인 성공: username={request.username}, session_id={session_id}"
            )
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"OUT: AuthService.login() - 로그인 오류 발생: username={request.username}, error={e}"
            )
            raise

    def logout(self, token: Optional[str] = None) -> LogoutResponseDto:
        """로그아웃 처리"""
        logger.info(f"IN: AuthService.logout() - 로그아웃 요청: token={token}")

        try:
            if token:
                logger.info(f"AuthService.logout() - 세션 제거 시작: token={token}")
                self.auth_dc.remove_session(token)
                self.auth_dao.deactivate_session(token)

            response = LogoutResponseDto(message="로그아웃 성공", success=True)
            logger.info(f"OUT: AuthService.logout() - 로그아웃 성공: token={token}")
            return response

        except Exception as e:
            logger.error(
                f"OUT: AuthService.logout() - 로그아웃 오류 발생: token={token}, error={e}"
            )
            raise

    def validate_session(self, token: str) -> bool:
        """세션 유효성 검증"""
        logger.info(
            f"IN: AuthService.validate_session() - 세션 검증 요청: token={token}"
        )
        try:
            result = (
                self.auth_dc.validate_session(token)
                and self.auth_dao.get_session(token) is not None
            )
            logger.info(
                f"OUT: AuthService.validate_session() - 세션 검증 완료: token={token}, valid={result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"OUT: AuthService.validate_session() - 세션 검증 오류: token={token}, error={e}"
            )
            raise

    def get_admin_info(self) -> dict:
        """관리자 정보 조회"""
        logger.info("IN: AuthService.get_admin_info() - 관리자 정보 조회 요청")
        try:
            dc_info = self.auth_dc.get_admin_config()
            dao_sessions = self.auth_dao.get_active_sessions()
            accounts = self.account_dao.get_all_accounts()

            response = {
                **dc_info,
                "db_sessions": dao_sessions,
                "accounts": accounts,
                "account_count": self.account_dao.get_account_count(),
            }
            logger.info("OUT: AuthService.get_admin_info() - 관리자 정보 조회 완료")
            return response
        except Exception as e:
            logger.error(
                f"OUT: AuthService.get_admin_info() - 관리자 정보 조회 오류: {e}"
            )
            raise
