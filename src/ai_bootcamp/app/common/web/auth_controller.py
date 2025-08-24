import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from ..business.aps.auth_service import AuthService
from ..transfer.auth_dto import (LoginRequestDto, LoginResponseDto,
                                 LogoutResponseDto)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["인증"])


class AuthController:
    """인증 관련 웹 컨트롤러"""

    def __init__(self):
        self.auth_service = AuthService()
        self.templates_path = (
            Path(__file__).parent.parent.parent.parent / "resources" / "templates"
        )

    @router.get("/login", response_class=HTMLResponse)
    async def login_page(self):
        """로그인 페이지"""
        logger.info("IN: AuthController.login_page() - 로그인 페이지 요청")
        try:
            response = FileResponse(str(self.templates_path / "login" / "index.html"))
            logger.info("OUT: AuthController.login_page() - 로그인 페이지 반환 성공")
            return response
        except Exception as e:
            logger.error(f"OUT: AuthController.login_page() - 오류 발생: {e}")
            raise

    @router.post("/login")
    async def login(self, request: LoginRequestDto) -> LoginResponseDto:
        """로그인 처리"""
        logger.info(
            f"IN: AuthController.login() - 로그인 요청: username={request.username}"
        )
        try:
            response = self.auth_service.login(request)
            logger.info(
                f"OUT: AuthController.login() - 로그인 처리 완료: username={request.username}"
            )
            return response
        except Exception as e:
            logger.error(
                f"OUT: AuthController.login() - 로그인 오류 발생: username={request.username}, error={e}"
            )
            raise

    @router.post("/logout")
    async def logout(self) -> LogoutResponseDto:
        """로그아웃 처리"""
        logger.info("IN: AuthController.logout() - 로그아웃 요청")
        try:
            response = self.auth_service.logout()
            logger.info("OUT: AuthController.logout() - 로그아웃 처리 완료")
            return response
        except Exception as e:
            logger.error(f"OUT: AuthController.logout() - 로그아웃 오류 발생: {e}")
            raise

    @router.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(self):
        """대시보드 페이지"""
        logger.info("IN: AuthController.dashboard() - 대시보드 페이지 요청")
        try:
            response = FileResponse(
                str(self.templates_path / "dashboard" / "index.html")
            )
            logger.info("OUT: AuthController.dashboard() - 대시보드 페이지 반환 성공")
            return response
        except Exception as e:
            logger.error(f"OUT: AuthController.dashboard() - 오류 발생: {e}")
            raise


# 컨트롤러 인스턴스 생성
auth_controller = AuthController()
