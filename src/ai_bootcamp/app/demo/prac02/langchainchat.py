#!/usr/bin/env python3
"""
LangChain Chat Demo - OpenAI API Version
Azure OpenAI에서 OpenAI API로 변환된 LangChain 채팅 데모
"""

import os
import logging
from typing import List, Tuple, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LangChainChatDemo:
    """LangChain을 사용한 OpenAI 채팅 데모 클래스"""
    
    def __init__(self, use_mock: bool = False):
        """
        LangChainChatDemo 초기화
        
        Args:
            use_mock (bool): Mock 모드 사용 여부 (API 할당량 초과 시 테스트용)
        """
        logger.info("IN: LangChainChatDemo.__init__() - LangChainChatDemo 초기화")
        
        self.use_mock = use_mock
        
        # OpenAI 환경 변수
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if not self.openai_api_key and not self.use_mock:
            logger.error("OUT: LangChainChatDemo.__init__() - OPENAI_API_KEY가 설정되지 않음")
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        if not self.use_mock:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                from langchain_openai import ChatOpenAI
                
                self.model = ChatOpenAI(
                    model=self.openai_model,
                    api_key=self.openai_api_key
                )
                logger.info("OUT: LangChainChatDemo.__init__() - LangChain OpenAI 클라이언트 초기화 성공")
            except ImportError as e:
                logger.error(f"OUT: LangChainChatDemo.__init__() - LangChain 라이브러리 import 오류: {e}")
                raise ImportError("langchain-openai 라이브러리가 설치되지 않았습니다. 'pip install langchain-openai'를 실행하세요.")
            except Exception as e:
                logger.error(f"OUT: LangChainChatDemo.__init__() - OpenAI 클라이언트 초기화 오류: {e}")
                raise
        else:
            logger.info("OUT: LangChainChatDemo.__init__() - Mock 모드로 초기화")
    
    def translate_text(self, text: str, target_language: str = "Korean") -> str:
        """
        텍스트 번역 (영어 -> 한국어)
        
        Args:
            text (str): 번역할 텍스트
            target_language (str): 목표 언어
            
        Returns:
            str: 번역된 텍스트
        """
        logger.info(f"IN: translate_text() - 번역 요청: text={text}, target_language={target_language}")
        
        if self.use_mock:
            # Mock 응답
            mock_translations = {
                "I love programming.": "저는 프로그래밍을 사랑합니다.",
                "Hello, world!": "안녕하세요, 세계!",
                "Python is amazing.": "파이썬은 놀라워요.",
                "Machine learning is fun.": "머신러닝은 재미있어요."
            }
            result = mock_translations.get(text, f"[Mock] '{text}'를 {target_language}로 번역")
            logger.info(f"OUT: translate_text() - Mock 번역 결과: {result}")
            return result
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            system_prompt = f"You are a helpful assistant that translates English to {target_language}. Translate the user sentence."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=text)
            ]
            
            logger.info(f"translate_text() - API 호출 시작: model={self.openai_model}")
            response = self.model.invoke(messages)
            
            result = response.content
            logger.info(f"OUT: translate_text() - 번역 성공: {result}")
            return result
            
        except Exception as e:
            logger.error(f"OUT: translate_text() - 번역 오류: {e}")
            raise
    
    def chat_conversation(self, messages: List[Tuple[str, str]]) -> List[str]:
        """
        대화형 채팅
        
        Args:
            messages (List[Tuple[str, str]]): 메시지 리스트 (role, content)
            
        Returns:
            List[str]: AI 응답 리스트
        """
        logger.info(f"IN: chat_conversation() - 대화 요청: messages_count={len(messages)}")
        
        if self.use_mock:
            # Mock 응답
            mock_responses = [
                "안녕하세요! 무엇을 도와드릴까요?",
                "프로그래밍에 대해 질문하시는군요. 어떤 부분이 궁금하신가요?",
                "파이썬은 매우 유연하고 강력한 프로그래밍 언어입니다.",
                "머신러닝과 AI에 관심이 있으시군요. 좋은 선택입니다!"
            ]
            responses = mock_responses[:len(messages)]
            logger.info(f"OUT: chat_conversation() - Mock 응답: {responses}")
            return responses
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            
            langchain_messages = []
            responses = []
            
            for role, content in messages:
                if role.lower() == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role.lower() == "human":
                    langchain_messages.append(HumanMessage(content=content))
                elif role.lower() == "ai":
                    langchain_messages.append(AIMessage(content=content))
            
            logger.info(f"chat_conversation() - API 호출 시작: model={self.openai_model}")
            response = self.model.invoke(langchain_messages)
            
            responses.append(response.content)
            logger.info(f"OUT: chat_conversation() - 대화 성공: {responses}")
            return responses
            
        except Exception as e:
            logger.error(f"OUT: chat_conversation() - 대화 오류: {e}")
            raise
    
    def test_translation(self) -> None:
        """번역 기능 테스트"""
        logger.info("IN: test_translation() - 번역 테스트 시작")
        
        print("🤖 LangChain 번역 데모 시작")
        print("=" * 50)
        
        test_texts = [
            "I love programming.",
            "Hello, world!",
            "Python is amazing.",
            "Machine learning is fun."
        ]
        
        for text in test_texts:
            try:
                print(f"\n📝 원문: {text}")
                translated = self.translate_text(text)
                print(f"🇰🇷 번역: {translated}")
            except Exception as e:
                print(f"❌ 번역 오류: {e}")
        
        print("\n" + "=" * 50)
        logger.info("OUT: test_translation() - 번역 테스트 완료")
    
    def test_conversation(self) -> None:
        """대화 기능 테스트"""
        logger.info("IN: test_conversation() - 대화 테스트 시작")
        
        print("🤖 LangChain 대화 데모 시작")
        print("=" * 50)
        
        conversation = [
            ("system", "You are a helpful programming assistant. Answer in Korean."),
            ("human", "안녕하세요! 프로그래밍에 대해 질문이 있어요."),
            ("human", "파이썬의 장점은 무엇인가요?"),
            ("human", "머신러닝을 시작하려면 어떻게 해야 하나요?")
        ]
        
        try:
            responses = self.chat_conversation(conversation)
            
            for i, (role, content) in enumerate(conversation):
                if role == "human":
                    print(f"\n👤 사용자: {content}")
                    if i < len(responses):
                        print(f"🤖 AI: {responses[i]}")
                        
        except Exception as e:
            print(f"❌ 대화 오류: {e}")
        
        print("\n" + "=" * 50)
        logger.info("OUT: test_conversation() - 대화 테스트 완료")


def main():
    """메인 함수"""
    logger.info("IN: main() - 프로그램 시작")
    
    try:
        print("🚀 LangChain OpenAI Chat Demo")
        print("=" * 50)
        
        # Mock 모드 확인 (환경 변수로 제어 가능)
        use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
        
        if use_mock:
            print("🔧 Mock 모드로 실행 중 (API 할당량 초과 시 테스트용)")
        
        # LangChainChatDemo 인스턴스 생성
        chat_demo = LangChainChatDemo(use_mock=use_mock)
        
        # 번역 테스트
        chat_demo.test_translation()
        
        print("\n" + "=" * 50)
        
        # 대화 테스트
        chat_demo.test_conversation()
        
        print("\n✅ 프로그램 실행 완료")
        logger.info("OUT: main() - 프로그램 완료")
        
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류 발생: {e}")
        logger.error(f"OUT: main() - 프로그램 오류: {e}")


if __name__ == "__main__":
    main() 