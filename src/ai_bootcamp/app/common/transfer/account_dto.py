from typing import List, Optional

from pydantic import BaseModel


class AccountDto(BaseModel):
    """계정 정보 DTO"""

    id: str
    name: str
    company: Optional[str] = None
    juso: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AccountCreateRequestDto(BaseModel):
    """계정 생성 요청 DTO"""

    name: str
    company: Optional[str] = None
    password: str
    juso: Optional[str] = None


class AccountCreateDto(BaseModel):
    """계정 생성 요청 DTO (기존 호환성)"""

    id: str
    name: str
    company: Optional[str] = None
    password: str
    juso: Optional[str] = None


class AccountUpdateRequestDto(BaseModel):
    """계정 수정 요청 DTO"""

    name: str
    company: Optional[str] = None
    password: str
    juso: Optional[str] = None


class AccountDeleteRequestDto(BaseModel):
    """계정 삭제 요청 DTO"""

    account_id: str


class AccountUpdateDto(BaseModel):
    """계정 수정 요청 DTO (기존 호환성)"""

    name: Optional[str] = None
    company: Optional[str] = None
    password: Optional[str] = None
    juso: Optional[str] = None


class AccountListResponseDto(BaseModel):
    """계정 목록 응답 DTO"""

    accounts: List[AccountDto]
    total_count: int
    status: str = "success"


class AccountListDto(BaseModel):
    """계정 목록 응답 DTO (기존 호환성)"""

    accounts: List[AccountDto]
    total_count: int


class AccountDetailResponseDto(BaseModel):
    """계정 상세 응답 DTO"""

    account: Optional[AccountDto] = None
    status: str = "success"
    message: Optional[str] = None


class AccountResponseDto(BaseModel):
    """계정 응답 DTO"""

    account: Optional[AccountDto] = None
    status: str = "success"
    message: str


class AccountResponseDtoOld(BaseModel):
    """계정 응답 DTO (기존 호환성)"""

    success: bool
    message: str
    data: Optional[AccountDto] = None
 