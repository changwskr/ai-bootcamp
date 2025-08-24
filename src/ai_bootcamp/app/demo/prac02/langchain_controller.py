#!/usr/bin/env python3
"""
LangChain Demo Web Controller
LangChain 데모 페이지를 위한 웹 컨트롤러
"""

import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/demo/prac02", tags=["demo"])

# 템플릿 설정
templates = Jinja2Templates(directory="src/ai_bootcamp/resources/templates")


@router.get("/langchain", response_class=HTMLResponse)
async def langchain_demo_page(request: Request):
    """
    LangChain 데모 페이지 렌더링
    
    Args:
        request (Request): FastAPI 요청 객체
        
    Returns:
        HTMLResponse: LangChain 데모 페이지
    """
    logger.info("IN: langchain_demo_page() - LangChain 데모 페이지 요청")
    
    try:
        response = templates.TemplateResponse(
            "demo/prac02/langchain.html",
            {"request": request}
        )
        logger.info("OUT: langchain_demo_page() - LangChain 데모 페이지 렌더링 성공")
        return response
        
    except Exception as e:
        logger.error(f"OUT: langchain_demo_page() - 페이지 렌더링 오류: {e}")
        raise 