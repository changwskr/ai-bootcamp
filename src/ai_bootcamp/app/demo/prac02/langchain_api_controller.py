#!/usr/bin/env python3
"""
LangChain API Controller
LangChain 기능을 위한 API 컨트롤러
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/api/langchain", tags=["langchain"])


class TranslationRequest(BaseModel):
    """번역 요청 DTO"""
    text: str
    target_language: str = "Korean"


class TranslationResponse(BaseModel):
    """번역 응답 DTO"""
    translation: str
    original_text: str
    target_language: str


class ChatMessage(BaseModel):
    """채팅 메시지 DTO"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """채팅 요청 DTO"""
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    """채팅 응답 DTO"""
    response: str
    conversation_length: int


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    텍스트 번역 API
    
    Args:
        request (TranslationRequest): 번역 요청
        
    Returns:
        TranslationResponse: 번역 결과
    """
    logger.info(f"IN: translate_text() - 번역 요청: text={request.text}, target_language={request.target_language}")
    
    try:
        # Mock 모드 확인
        import os
        use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
        
        if use_mock:
            # Mock 응답
            mock_translations = {
                "I love programming.": "저는 프로그래밍을 사랑합니다.",
                "Hello, world!": "안녕하세요, 세계!",
                "Python is amazing.": "파이썬은 놀라워요.",
                "Machine learning is fun.": "머신러닝은 재미있어요."
            }
            translation = mock_translations.get(request.text, f"[Mock] '{request.text}'를 {request.target_language}로 번역")
            
            response = TranslationResponse(
                translation=translation,
                original_text=request.text,
                target_language=request.target_language
            )
            
            logger.info(f"OUT: translate_text() - Mock 번역 성공: {translation}")
            return response
        else:
            # 실제 LangChain 데모 인스턴스 생성
            from .langchainchat import LangChainChatDemo
            
            chat_demo = LangChainChatDemo(use_mock=False)
            
            # 번역 실행
            translation = chat_demo.translate_text(request.text, request.target_language)
            
            response = TranslationResponse(
                translation=translation,
                original_text=request.text,
                target_language=request.target_language
            )
            
            logger.info(f"OUT: translate_text() - 실제 번역 성공: {translation}")
            return response
        
    except Exception as e:
        logger.error(f"OUT: translate_text() - 번역 오류: {e}")
        raise HTTPException(status_code=500, detail=f"번역 중 오류가 발생했습니다: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_conversation(request: ChatRequest):
    """
    대화형 채팅 API
    
    Args:
        request (ChatRequest): 채팅 요청
        
    Returns:
        ChatResponse: AI 응답
    """
    logger.info(f"IN: chat_conversation() - 채팅 요청: messages_count={len(request.messages)}")
    
    try:
        # Mock 모드 확인
        import os
        use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
        
        if use_mock:
            # Mock 응답
            mock_responses = [
                "안녕하세요! 무엇을 도와드릴까요?",
                "프로그래밍에 대해 질문하시는군요. 어떤 부분이 궁금하신가요?",
                "파이썬은 매우 유연하고 강력한 프로그래밍 언어입니다.",
                "머신러닝과 AI에 관심이 있으시군요. 좋은 선택입니다!",
                "코딩을 배우는 것은 정말 재미있고 유용한 기술입니다.",
                "AI 기술은 앞으로 더욱 발전할 것으로 예상됩니다."
            ]
            
            # 메시지 개수에 따라 다른 응답 반환
            response_index = min(len(request.messages) - 1, len(mock_responses) - 1)
            ai_response = mock_responses[response_index] if response_index >= 0 else mock_responses[0]
            
            response = ChatResponse(
                response=ai_response,
                conversation_length=len(request.messages)
            )
            
            logger.info(f"OUT: chat_conversation() - Mock 채팅 성공: {ai_response}")
            return response
        else:
            # 실제 LangChain 데모 인스턴스 생성
            from .langchainchat import LangChainChatDemo
            
            chat_demo = LangChainChatDemo(use_mock=False)
            
            # 메시지 형식 변환
            messages = [(msg.role, msg.content) for msg in request.messages]
            
            # 채팅 실행
            responses = chat_demo.chat_conversation(messages)
            
            # 마지막 응답 반환
            ai_response = responses[-1] if responses else "죄송합니다. 응답을 생성할 수 없습니다."
            
            response = ChatResponse(
                response=ai_response,
                conversation_length=len(request.messages)
            )
            
            logger.info(f"OUT: chat_conversation() - 실제 채팅 성공: {ai_response}")
            return response
        
    except Exception as e:
        logger.error(f"OUT: chat_conversation() - 채팅 오류: {e}")
        raise HTTPException(status_code=500, detail=f"채팅 중 오류가 발생했습니다: {str(e)}")


@router.get("/health")
async def health_check():
    """
    LangChain API 상태 확인
    
    Returns:
        Dict[str, Any]: 상태 정보
    """
    logger.info("IN: health_check() - LangChain API 상태 확인")
    
    try:
        # LangChain 라이브러리 import 확인
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_openai import ChatOpenAI
            langchain_available = True
        except ImportError:
            langchain_available = False
        
        # OpenAI API 키 확인
        import os
        openai_key_available = bool(os.getenv("OPENAI_API_KEY"))
        
        status = {
            "status": "healthy",
            "langchain_available": langchain_available,
            "openai_key_available": openai_key_available,
            "mock_mode": os.getenv("USE_MOCK", "false").lower() == "true"
        }
        
        logger.info(f"OUT: health_check() - 상태 확인 완료: {status}")
        return status
        
    except Exception as e:
        logger.error(f"OUT: health_check() - 상태 확인 오류: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 중 오류가 발생했습니다: {str(e)}") 