import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from ..business.aps.account_service import account_service
from ..transfer.account_dto import (AccountCreateRequestDto, AccountDto,
                                    AccountListResponseDto, AccountResponseDto,
                                    AccountUpdateRequestDto)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/accounts", tags=["계정 관리"])


class AccountController:
    """계정 관련 웹 컨트롤러"""

    def __init__(self):
        self.templates_path = (
            Path(__file__).parent.parent.parent.parent / "resources" / "templates"
        )

    @router.get("/")
    async def get_accounts(self) -> AccountListResponseDto:
        """모든 계정 목록 조회"""
        logger.info("IN: AccountController.get_accounts() - 계정 목록 조회 요청")
        try:
            response = await account_service.get_account_list()
            logger.info(
                f"OUT: AccountController.get_accounts() - 계정 목록 조회 완료: count={response.total_count}, response_type={type(response)}"
            )
            logger.info(f"OUT: AccountController.get_accounts() - response data: {response}")
            return response
        except Exception as e:
            logger.error(
                f"OUT: AccountController.get_accounts() - 계정 목록 조회 오류: {e}"
            )
            import traceback
            logger.error(f"OUT: AccountController.get_accounts() - 오류 상세: {traceback.format_exc()}")
            raise

    @router.get("/{account_id}")
    async def get_account(self, account_id: str) -> AccountResponseDto:
        """특정 계정 조회"""
        logger.info(
            f"IN: AccountController.get_account() - 계정 조회 요청: account_id={account_id}"
        )
        try:
            response = await account_service.get_account_detail(account_id)
            logger.info(
                f"OUT: AccountController.get_account() - 계정 조회 완료: account_id={account_id}"
            )
            return response
        except Exception as e:
            logger.error(
                f"OUT: AccountController.get_account() - 계정 조회 오류: account_id={account_id}, error={e}"
            )
            raise

    @router.post("/")
    async def create_account(self, request: AccountCreateRequestDto) -> AccountResponseDto:
        """새 계정 생성"""
        logger.info(
            f"IN: AccountController.create_account() - 계정 생성 요청: name={request.name}"
        )
        try:
            response = await account_service.create_account(request)
            logger.info(
                f"OUT: AccountController.create_account() - 계정 생성 완료: name={request.name}"
            )
            return response
        except Exception as e:
            logger.error(
                f"OUT: AccountController.create_account() - 계정 생성 오류: name={request.name}, error={e}"
            )
            raise

    @router.put("/{account_id}")
    async def update_account(
        self, account_id: str, request: AccountUpdateRequestDto
    ) -> AccountResponseDto:
        """계정 정보 수정"""
        logger.info(
            f"IN: AccountController.update_account() - 계정 수정 요청: account_id={account_id}"
        )
        try:
            response = await account_service.update_account(account_id, request)
            logger.info(
                f"OUT: AccountController.update_account() - 계정 수정 완료: account_id={account_id}"
            )
            return response
        except Exception as e:
            logger.error(
                f"OUT: AccountController.update_account() - 계정 수정 오류: account_id={account_id}, error={e}"
            )
            raise

    @router.delete("/{account_id}")
    async def delete_account(self, account_id: str) -> AccountResponseDto:
        """계정 삭제"""
        logger.info(
            f"IN: AccountController.delete_account() - 계정 삭제 요청: account_id={account_id}"
        )
        try:
            response = await account_service.delete_account(account_id)
            logger.info(
                f"OUT: AccountController.delete_account() - 계정 삭제 완료: account_id={account_id}"
            )
            return response
        except Exception as e:
            logger.error(
                f"OUT: AccountController.delete_account() - 계정 삭제 오류: account_id={account_id}, error={e}"
            )
            raise


    async def accounts_page(self):
        """계정 관리 페이지"""
        logger.info("IN: AccountController.accounts_page() - 계정 관리 페이지 요청")
        try:
            response = FileResponse(
                str(self.templates_path / "accounts" / "index.html")
            )
            logger.info("OUT: AccountController.accounts_page() - 계정 관리 페이지 반환 성공")
            return response
        except Exception as e:
            logger.error(f"OUT: AccountController.accounts_page() - 오류 발생: {e}")
            raise


# 컨트롤러 인스턴스 생성
account_controller = AccountController()
 