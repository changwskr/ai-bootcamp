from typing import Optional

from pydantic import BaseModel


class LoginRequestDto(BaseModel):
    """로그인 요청 DTO"""

    username: str
    password: str


class LoginResponseDto(BaseModel):
    """로그인 응답 DTO"""

    message: str
    success: bool
    token: Optional[str] = None


class LogoutRequestDto(BaseModel):
    """로그아웃 요청 DTO"""

    token: Optional[str] = None


class LogoutResponseDto(BaseModel):
    """로그아웃 응답 DTO"""

    message: str
    success: bool
