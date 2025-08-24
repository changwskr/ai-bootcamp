#!/usr/bin/env python3
"""
Account Domain Component (DC)
계정 관련 도메인 로직을 처리하는 컴포넌트
"""

import logging
from typing import List, Optional

from ...transfer.account_dto import AccountDto

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AccountDC:
    """계정 도메인 컴포넌트"""

    def __init__(self):
        logger.info("IN: AccountDC.__init__() - AccountDC 초기화")
        from .repository.account_dao import AccountDAO
        self.account_dao = AccountDAO()
        logger.info("OUT: AccountDC.__init__() - AccountDC 초기화 완료")

    async def get_all_accounts(self) -> List[AccountDto]:
        """모든 계정 조회"""
        logger.info("IN: AccountDC.get_all_accounts() - 모든 계정 조회 요청")
        try:
            account_dicts = self.account_dao.get_all_accounts()
            accounts = []
            for account_dict in account_dicts:
                account = AccountDto(
                    id=account_dict["id"],
                    name=account_dict["name"],
                    company=account_dict.get("company"),
                    juso=account_dict.get("juso"),
                    created_at=account_dict.get("created_at"),
                    updated_at=account_dict.get("updated_at")
                )
                accounts.append(account)
            logger.info(f"OUT: AccountDC.get_all_accounts() - 계정 조회 성공: {len(accounts)}개")
            return accounts
        except Exception as e:
            logger.error(f"OUT: AccountDC.get_all_accounts() - 오류 발생: {e}")
            raise

    async def get_account_by_id(self, account_id: str) -> Optional[AccountDto]:
        """ID로 계정 조회"""
        logger.info(f"IN: AccountDC.get_account_by_id() - 계정 조회 요청: account_id={account_id}")
        try:
            account_dict = self.account_dao.get_account_by_id(account_id)
            if account_dict:
                account = AccountDto(
                    id=account_dict["id"],
                    name=account_dict["name"],
                    company=account_dict.get("company"),
                    juso=account_dict.get("juso"),
                    created_at=account_dict.get("created_at"),
                    updated_at=account_dict.get("updated_at")
                )
                logger.info(f"OUT: AccountDC.get_account_by_id() - 계정 조회 성공: {account_id}")
                return account
            else:
                logger.info(f"OUT: AccountDC.get_account_by_id() - 계정 없음: {account_id}")
                return None
        except Exception as e:
            logger.error(f"OUT: AccountDC.get_account_by_id() - 오류 발생: {e}")
            raise

    async def create_account(self, name: str, company: str, password: str, juso: str) -> AccountDto:
        """계정 생성"""
        logger.info(f"IN: AccountDC.create_account() - 계정 생성 요청: name={name}, company={company}")
        try:
            # 비즈니스 로직 검증
            if not name or not password:
                raise ValueError("이름과 비밀번호는 필수입니다.")
            
            if len(password) < 4:
                raise ValueError("비밀번호는 최소 4자 이상이어야 합니다.")
            
            account = self.account_dao.create_account(name, company, password, juso)
            logger.info(f"OUT: AccountDC.create_account() - 계정 생성 성공: {account.id}")
            return account
        except Exception as e:
            logger.error(f"OUT: AccountDC.create_account() - 오류 발생: {e}")
            raise

    async def update_account(self, account_id: str, name: str, company: str, password: str, juso: str) -> Optional[AccountDto]:
        """계정 수정"""
        logger.info(f"IN: AccountDC.update_account() - 계정 수정 요청: account_id={account_id}")
        try:
            # 기존 계정 확인
            existing_account = self.account_dao.get_account_by_id(account_id)
            if not existing_account:
                logger.info(f"OUT: AccountDC.update_account() - 수정할 계정 없음: {account_id}")
                return None
            
            # 비즈니스 로직 검증
            if not name or not password:
                raise ValueError("이름과 비밀번호는 필수입니다.")
            
            if len(password) < 4:
                raise ValueError("비밀번호는 최소 4자 이상이어야 합니다.")
            
            account = self.account_dao.update_account(account_id, name, company, password, juso)
            logger.info(f"OUT: AccountDC.update_account() - 계정 수정 성공: {account_id}")
            return account
        except Exception as e:
            logger.error(f"OUT: AccountDC.update_account() - 오류 발생: {e}")
            raise

    async def delete_account(self, account_id: str) -> bool:
        """계정 삭제"""
        logger.info(f"IN: AccountDC.delete_account() - 계정 삭제 요청: account_id={account_id}")
        try:
            # 기존 계정 확인
            existing_account = self.account_dao.get_account_by_id(account_id)
            if not existing_account:
                logger.info(f"OUT: AccountDC.delete_account() - 삭제할 계정 없음: {account_id}")
                return False
            
            # admin 계정은 삭제 불가
            if account_id == "admin":
                raise ValueError("admin 계정은 삭제할 수 없습니다.")
            
            success = self.account_dao.delete_account(account_id)
            logger.info(f"OUT: AccountDC.delete_account() - 계정 삭제 성공: {account_id}")
            return success
        except Exception as e:
            logger.error(f"OUT: AccountDC.delete_account() - 오류 발생: {e}")
            raise

    async def validate_account(self, account_id: str, password: str) -> bool:
        """계정 인증"""
        logger.info(f"IN: AccountDC.validate_account() - 계정 인증 요청: account_id={account_id}")
        try:
            account = self.account_dao.get_account_by_id(account_id)
            if not account:
                logger.info(f"OUT: AccountDC.validate_account() - 계정 없음: {account_id}")
                return False
            
            is_valid = account.password == password
            logger.info(f"OUT: AccountDC.validate_account() - 인증 결과: {account_id} = {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"OUT: AccountDC.validate_account() - 오류 발생: {e}")
            raise


# DC 인스턴스 생성
account_dc = AccountDC() 