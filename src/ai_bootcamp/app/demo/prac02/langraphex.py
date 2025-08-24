#!/usr/bin/env python3
"""
LangGraph 예제
LangGraph를 사용한 워크플로우 데모 (OpenAI API 연동)
"""

import logging
import os
from typing import TypedDict
from langgraph.graph import StateGraph
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 상태 정의
class WorkflowState(TypedDict):
    query: str
    result: str
    summary: str


def main():
    """메인 함수"""
    logger.info("IN: main() - LangGraph 예제 시작")
    
    try:
        # 그래프 생성
        workflow = StateGraph(WorkflowState)
        
        # 노드 정의
        def search_node(state):
            logger.info(f"IN: search_node() - OpenAI API 호출: query={state['query']}")
            try:
                # OpenAI API 호출
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 유용한 정보를 제공하는 AI 어시스턴트입니다. 사용자의 질문에 대해 자세하고 정확한 답변을 제공해주세요."},
                        {"role": "user", "content": state['query']}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                result = response.choices[0].message.content
                logger.info(f"OUT: search_node() - OpenAI API 응답 완료: {result[:100]}...")
                return {"result": result}
            except Exception as e:
                logger.error(f"OUT: search_node() - OpenAI API 오류: {e}")
                error_msg = f"OpenAI API 호출 중 오류가 발생했습니다: {e}"
                return {"result": error_msg}
        
        def summarize_node(state):
            logger.info(f"IN: summarize_node() - 요약 실행: result={state['result'][:100]}...")
            try:
                # OpenAI API로 요약 생성
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "주어진 텍스트를 간결하고 명확하게 요약해주세요."},
                        {"role": "user", "content": f"다음 텍스트를 요약해주세요:\n\n{state['result']}"}
                    ],
                    max_tokens=200,
                    temperature=0.5
                )
                summary = response.choices[0].message.content
                logger.info(f"OUT: summarize_node() - 요약 완료: {summary[:100]}...")
                return {"summary": summary}
            except Exception as e:
                logger.error(f"OUT: summarize_node() - OpenAI API 오류: {e}")
                error_msg = f"요약 생성 중 오류가 발생했습니다: {e}"
                return {"summary": error_msg}
        
        # 노드 등록
        workflow.add_node("search", search_node)
        workflow.add_node("summarize", summarize_node)
        
        # 연결 정의
        workflow.add_edge("search", "summarize")
        
        # 시작점 설정 (START에서 search로)
        workflow.set_entry_point("search")
        
        # 워크플로우 컴파일
        app = workflow.compile()
        logger.info("OUT: main() - 워크플로우 컴파일 완료")
        
        print("=" * 60)
        print("🎯 LangGraph + OpenAI API 워크플로우 데모")
        print("=" * 60)
        print("💡 사용법:")
        print("   - 질문을 입력하면 OpenAI API로 답변 → 요약 워크플로우가 실행됩니다")
        print("   - 'END'를 입력하면 프로그램이 종료됩니다")
        print("🔑 OpenAI API Key 필요: .env 파일에 OPENAI_API_KEY 설정")
        print("=" * 60)
        
        # 대화형 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = input("\n🤔 질문을 입력하세요 (종료: END): ").strip()
                
                # END 입력 시 종료
                if user_input.upper() == "END":
                    logger.info("IN: main() - 사용자가 END를 입력하여 종료")
                    print("\n👋 LangGraph 데모를 종료합니다. 감사합니다!")
                    break
                
                # 빈 입력 처리
                if not user_input:
                    print("⚠️  질문을 입력해주세요.")
                    continue
                
                logger.info(f"IN: main() - 사용자 입력: {user_input}")
                
                # 워크플로우 실행
                result = app.invoke({"query": user_input})
                logger.info(f"OUT: main() - 워크플로우 실행 완료: {result}")
                
                # 결과 출력
                print("\n" + "=" * 50)
                print("🎯 OpenAI API 워크플로우 실행 결과")
                print("=" * 50)
                print(f"📝 원본 쿼리: {result['query']}")
                print(f"🤖 OpenAI 답변: {result['result']}")
                print(f"📋 AI 요약: {result['summary']}")
                print("=" * 50)
                
            except KeyboardInterrupt:
                logger.info("IN: main() - Ctrl+C로 종료")
                print("\n\n👋 프로그램이 중단되었습니다. 감사합니다!")
                break
            except Exception as e:
                logger.error(f"OUT: main() - 루프 내 오류 발생: {e}")
                print(f"❌ 오류 발생: {e}")
                print("다시 시도해주세요.")
        
    except Exception as e:
        logger.error(f"OUT: main() - 오류 발생: {e}")
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
