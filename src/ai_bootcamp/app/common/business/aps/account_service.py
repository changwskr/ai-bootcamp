#!/usr/bin/env python3
"""
Account Service (APS)
계정 관리 비즈니스 로직을 처리하는 애플리케이션 서비스
"""

import logging
from typing import List, Optional

from ...transfer.account_dto import (
    AccountListResponseDto,
    AccountDetailResponseDto,
    AccountCreateRequestDto,
    AccountUpdateRequestDto,
    AccountDeleteRequestDto,
    AccountResponseDto
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AccountService:
    """계정 관리 서비스"""

    def __init__(self):
        logger.info("IN: AccountService.__init__() - AccountService 초기화")
        from ..dc.account_dc import AccountDC
        self.account_dc = AccountDC()
        logger.info("OUT: AccountService.__init__() - AccountService 초기화 완료")

    async def get_account_list(self) -> AccountListResponseDto:
        """계정 목록 조회"""
        logger.info("IN: AccountService.get_account_list() - 계정 목록 조회 요청")
        try:
            accounts = self.account_dc.get_all_accounts()
            logger.info(f"AccountService.get_account_list() - accounts type: {type(accounts)}, count: {len(accounts)}")
            logger.info(f"AccountService.get_account_list() - accounts data: {accounts}")
            
            response = AccountListResponseDto(
                accounts=accounts,
                total_count=len(accounts),
                status="success"
            )
            logger.info(f"OUT: AccountService.get_account_list() - 계정 목록 조회 성공: {len(accounts)}개, response_type: {type(response)}")
            return response
        except Exception as e:
            logger.error(f"OUT: AccountService.get_account_list() - 오류 발생: {e}")
            raise

    async def get_account_detail(self, account_id: str) -> AccountDetailResponseDto:
        """계정 상세 조회"""
        logger.info(f"IN: AccountService.get_account_detail() - 계정 상세 조회 요청: account_id={account_id}")
        try:
            account = self.account_dc.get_account_by_id(account_id)
            if not account:
                response = AccountDetailResponseDto(
                    account=None,
                    status="not_found",
                    message="계정을 찾을 수 없습니다."
                )
                logger.info(f"OUT: AccountService.get_account_detail() - 계정 없음: {account_id}")
                return response
            
            response = AccountDetailResponseDto(
                account=account,
                status="success"
            )
            logger.info(f"OUT: AccountService.get_account_detail() - 계정 상세 조회 성공: {account_id}")
            return response
        except Exception as e:
            logger.error(f"OUT: AccountService.get_account_detail() - 오류 발생: {e}")
            raise

    async def create_account(self, request: AccountCreateRequestDto) -> AccountResponseDto:
        """계정 생성"""
        logger.info(f"IN: AccountService.create_account() - 계정 생성 요청: name={request.name}")
        try:
            account = self.account_dc.create_account(
                name=request.name,
                company=request.company,
                password=request.password,
                juso=request.juso
            )
            response = AccountResponseDto(
                account=account,
                status="success",
                message="계정이 성공적으로 생성되었습니다."
            )
            logger.info(f"OUT: AccountService.create_account() - 계정 생성 성공: {account.id}")
            return response
        except Exception as e:
            logger.error(f"OUT: AccountService.create_account() - 오류 발생: {e}")
            raise

    async def update_account(self, account_id: str, request: AccountUpdateRequestDto) -> AccountResponseDto:
        """계정 수정"""
        logger.info(f"IN: AccountService.update_account() - 계정 수정 요청: account_id={account_id}")
        try:
            account = self.account_dc.update_account(
                account_id=account_id,
                name=request.name,
                company=request.company,
                password=request.password,
                juso=request.juso
            )
            if not account:
                response = AccountResponseDto(
                    account=None,
                    status="not_found",
                    message="수정할 계정을 찾을 수 없습니다."
                )
                logger.info(f"OUT: AccountService.update_account() - 계정 없음: {account_id}")
                return response
            
            response = AccountResponseDto(
                account=account,
                status="success",
                message="계정이 성공적으로 수정되었습니다."
            )
            logger.info(f"OUT: AccountService.update_account() - 계정 수정 성공: {account_id}")
            return response
        except Exception as e:
            logger.error(f"OUT: AccountService.update_account() - 오류 발생: {e}")
            raise

    async def delete_account(self, account_id: str) -> AccountResponseDto:
        """계정 삭제"""
        logger.info(f"IN: AccountService.delete_account() - 계정 삭제 요청: account_id={account_id}")
        try:
            success = self.account_dc.delete_account(account_id)
            if not success:
                response = AccountResponseDto(
                    account=None,
                    status="not_found",
                    message="삭제할 계정을 찾을 수 없습니다."
                )
                logger.info(f"OUT: AccountService.delete_account() - 계정 없음: {account_id}")
                return response
            
            response = AccountResponseDto(
                account=None,
                status="success",
                message="계정이 성공적으로 삭제되었습니다."
            )
            logger.info(f"OUT: AccountService.delete_account() - 계정 삭제 성공: {account_id}")
            return response
        except Exception as e:
            logger.error(f"OUT: AccountService.delete_account() - 오류 발생: {e}")
            raise


# 서비스 인스턴스 생성
account_service = AccountService() 