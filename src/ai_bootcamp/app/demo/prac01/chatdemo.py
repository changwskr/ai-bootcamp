import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenAI 환경 변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_GPT4 = os.getenv("OPENAI_MODEL_GPT4", "gpt-4")
OPENAI_MODEL_GPT35 = os.getenv("OPENAI_MODEL_GPT35", "gpt-3.5-turbo")
OPENAI_MODEL_GPT4O = os.getenv("OPENAI_MODEL_GPT4O", "gpt-4o")
OPENAI_MODEL_GPT4O_MINI = os.getenv("OPENAI_MODEL_GPT4O_MINI", "gpt-4o-mini")

class ChatDemo:
    """OpenAI 채팅 데모 클래스"""
    
    def __init__(self):
        """초기화"""
        logger.info("IN: ChatDemo.__init__() - ChatDemo 초기화")
        
        if not OPENAI_API_KEY:
            logger.error("OUT: ChatDemo.__init__() - OPENAI_API_KEY가 설정되지 않음")
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OUT: ChatDemo.__init__() - OpenAI 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"OUT: ChatDemo.__init__() - OpenAI 클라이언트 초기화 실패: {e}")
            raise
    
    def chat_completion(
        self, user_message: str, model: str | None = None, system_message: str | None = None
    ) -> dict:
        """채팅 완성 API 호출"""
        logger.info(f"IN: ChatDemo.chat_completion() - 채팅 요청: model={model}, message={user_message[:50]}...")
        
        try:
            # 기본 모델 설정
            if not model:
                model = OPENAI_MODEL_GPT4O_MINI
            
            # 기본 시스템 메시지 설정
            if not system_message:
                system_message = "You are a helpful assistant."
            
            # 메시지 구성
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            logger.info(f"ChatDemo.chat_completion() - API 호출 시작: model={model}")
            
            try:
                # OpenAI API 호출
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                
                # 응답 데이터 구성
                result = {
                    "content": response.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason
                }
                
                logger.info(f"OUT: ChatDemo.chat_completion() - 채팅 완료: tokens={result['usage']['total_tokens']}")
                return result
                
            except Exception as api_error:
                # API 오류 시 모의 응답 반환
                logger.warning(f"API 호출 실패, 모의 응답 사용: {api_error}")
                
                mock_response = {
                    "content": f"[모의 응답] {user_message}에 대한 답변입니다. (API 할당량 초과로 인한 테스트 응답)",
                    "usage": {
                        "prompt_tokens": len(user_message),
                        "completion_tokens": 50,
                        "total_tokens": len(user_message) + 50
                    },
                    "model": model or "gpt-4o-mini",
                    "finish_reason": "stop"
                }
                
                logger.info(f"OUT: ChatDemo.chat_completion() - 모의 응답 완료")
                return mock_response
            
        except Exception as e:
            logger.error(f"OUT: ChatDemo.chat_completion() - 채팅 오류 발생: {e}")
            raise
    
    def get_available_models(self) -> list:
        """사용 가능한 모델 목록 조회"""
        logger.info("IN: ChatDemo.get_available_models() - 모델 목록 조회")
        
        try:
            models = self.client.models.list()
            model_list = [model.id for model in models.data]
            logger.info(f"OUT: ChatDemo.get_available_models() - 모델 목록 조회 완료: count={len(model_list)}")
            return model_list
        except Exception as e:
            logger.error(f"OUT: ChatDemo.get_available_models() - 모델 목록 조회 오류: {e}")
            raise
    
    def test_chat(self, message: str = "안녕하세요! 간단한 자기소개를 해주세요.") -> None:
        """채팅 테스트 실행"""
        logger.info(f"IN: ChatDemo.test_chat() - 채팅 테스트: message={message}")
        
        try:
            print("🤖 OpenAI 채팅 데모 시작")
            print("=" * 50)
            
            # 채팅 완성 호출
            result = self.chat_completion(message)
            
            print(f"📝 사용자 메시지: {message}")
            print(f"🤖 AI 응답: {result['content']}")
            print(f"📊 토큰 사용량: {result['usage']}")
            print(f"🔧 모델: {result['model']}")
            print(f"✅ 완료 이유: {result['finish_reason']}")
            
            logger.info("OUT: ChatDemo.test_chat() - 채팅 테스트 완료")
            
        except Exception as e:
            logger.error(f"OUT: ChatDemo.test_chat() - 채팅 테스트 오류: {e}")
            print(f"❌ 오류 발생: {e}")

def main():
    """메인 함수"""
    logger.info("IN: main() - 프로그램 시작")
    
    try:
        # ChatDemo 인스턴스 생성
        chat_demo = ChatDemo()
        
        # 기본 채팅 테스트
        chat_demo.test_chat()
        
        # 추가 테스트 (다른 모델 사용)
        print("\n" + "=" * 50)
        print("🔄 다른 모델로 테스트")
        
        # GPT-4o Mini로 테스트
        result = chat_demo.chat_completion(
            "파이썬의 장점을 3가지 설명해주세요.",
            model=OPENAI_MODEL_GPT4O_MINI,
            system_message="You are a helpful programming assistant."
        )
        
        print(f"🤖 AI 응답 (GPT-4o Mini): {result['content']}")
        print(f"📊 토큰 사용량: {result['usage']}")
        
        logger.info("OUT: main() - 프로그램 완료")
        
    except Exception as e:
        logger.error(f"OUT: main() - 프로그램 오류: {e}")
        print(f"❌ 프로그램 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
 