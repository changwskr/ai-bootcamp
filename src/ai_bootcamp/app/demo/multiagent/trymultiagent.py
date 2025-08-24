#!/usr/bin/env python3
"""
멀티에이전트 시스템 - Supervisor 기반 워커 관리
참조 소스를 기반으로 한 LangGraph 멀티에이전트 구현
"""

import logging
import os
from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import MessagesState, END
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import create_react_agent
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
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# 워커 멤버 정의
members = ["cafeteria", "schedule"]

# 시스템 프롬프트 정의
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

# 라우터 옵션 정의
options = members + ["FINISH"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal[*options]

class State(MessagesState):
    next: str

# 도구 정의
@tool
def get_cafeteria_menu() -> str:
    """이번 주 구내식당 메뉴를 반환합니다."""
    logger.info("IN: get_cafeteria_menu() - 구내식당 메뉴 조회")
    menu = """이번 주 구내식당 메뉴:

월요일: 김치찌개, 계란말이, 시금치나물
화요일: 된장찌개, 돈까스, 김치
수요일: 순두부찌개, 제육볶음, 멸치볶음
목요일: 미역국, 삼겹살구이, 깍두기
금요일: 비빔밥, 계란국, 김치

오늘의 추천: 된장찌개 (칼로리: 350kcal)"""
    
    logger.info("OUT: get_cafeteria_menu() - 메뉴 조회 완료")
    return menu

@tool
def get_schedule() -> str:
    """현재 남아있는 일정을 반환합니다."""
    logger.info("IN: get_schedule() - 일정 조회")
    schedule = """현재 남아있는 일정:

오늘 (8월 20일):
- 14:00-15:00: 팀 미팅
- 16:00-17:00: 고객사 미팅

내일 (8월 21일):
- 10:00-11:00: 프로젝트 리뷰
- 14:00-16:00: 개발 세미나

이번 주:
- 8월 22일: 휴가
- 8월 23일: 15:00-17:00 클라이언트 미팅"""
    
    logger.info("OUT: get_schedule() - 일정 조회 완료")
    return schedule

def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
    """Supervisor 노드: 다음 워커를 결정하고 라우팅"""
    logger.info("IN: supervisor_node() - 워커 라우팅 결정")
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        
        if goto == "FINISH":
            goto = END
            logger.info("OUT: supervisor_node() - 작업 완료, 종료")
        else:
            logger.info(f"OUT: supervisor_node() - {goto} 워커로 라우팅")
        
        return Command(goto=goto, update={"next": goto})
        
    except Exception as e:
        logger.error(f"OUT: supervisor_node() - 오류 발생: {e}")
        return Command(goto=END, update={"next": "error"})

# 구내식당 에이전트 생성
cafeteria_agent = create_react_agent(
    llm, 
    tools=[get_cafeteria_menu], 
    prompt="당신은 구내식당을 관리하는 영양사입니다. 사용자에게 이번 주의 식단을 알려줄 수 있습니다."
)

def cafeteria_node(state: State) -> Command[Literal["supervisor"]]:
    """구내식당 워커 노드"""
    logger.info("IN: cafeteria_node() - 구내식당 에이전트 실행")
    
    try:
        result = cafeteria_agent.invoke(state)
        logger.info("OUT: cafeteria_node() - 구내식당 에이전트 완료")
        
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="cafeteria")
                ]
            },
            goto="supervisor",
        )
    except Exception as e:
        logger.error(f"OUT: cafeteria_node() - 오류 발생: {e}")
        return Command(
            update={
                "messages": [
                    HumanMessage(content="구내식당 메뉴 조회 중 오류가 발생했습니다.", name="cafeteria")
                ]
            },
            goto="supervisor",
        )

# 일정 관리 에이전트 생성
schedule_agent = create_react_agent(
    llm, 
    tools=[get_schedule], 
    prompt="당신은 사용자의 일정을 관리하는 비서입니다. 사용자에게 현재 남아있는 일정을 안내합니다."
)

def schedule_node(state: State) -> Command[Literal["supervisor"]]:
    """일정 관리 워커 노드"""
    logger.info("IN: schedule_node() - 일정 관리 에이전트 실행")
    
    try:
        result = schedule_agent.invoke(state)
        logger.info("OUT: schedule_node() - 일정 관리 에이전트 완료")
        
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="schedule")
                ]
            },
            goto="supervisor",
        )
    except Exception as e:
        logger.error(f"OUT: schedule_node() - 오류 발생: {e}")
        return Command(
            update={
                "messages": [
                    HumanMessage(content="일정 조회 중 오류가 발생했습니다.", name="schedule")
                ]
            },
            goto="supervisor",
        )

def main():
    """메인 함수"""
    logger.info("IN: main() - 멀티에이전트 시스템 시작")
    
    try:
        # 그래프 빌더 생성
        builder = StateGraph(State)
        
        # 엣지 및 노드 추가
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", supervisor_node)
        builder.add_node("cafeteria", cafeteria_node)
        builder.add_node("schedule", schedule_node)
        
        # 그래프 컴파일
        graph = builder.compile()
        logger.info("OUT: main() - 그래프 컴파일 완료")
        
        print("=" * 70)
        print("🎯 멀티에이전트 시스템 - Supervisor 기반 워커 관리")
        print("=" * 70)
        print("💡 워커 구성:")
        print("   - cafeteria: 구내식당 메뉴 관리")
        print("   - schedule: 일정 관리")
        print("💡 사용법:")
        print("   - '메뉴' 또는 '식당' 관련 질문 → cafeteria 워커")
        print("   - '일정' 또는 '스케줄' 관련 질문 → schedule 워커")
        print("   - '종료' 또는 '끝' → 작업 완료")
        print("🔑 OpenAI API Key 필요: .env 파일에 OPENAI_API_KEY 설정")
        print("=" * 70)
        
        # 대화형 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = input("\n🤔 질문을 입력하세요 (종료: END): ").strip()
                
                # END 입력 시 종료
                if user_input.upper() == "END":
                    logger.info("IN: main() - 사용자가 END를 입력하여 종료")
                    print("\n👋 멀티에이전트 시스템을 종료합니다. 감사합니다!")
                    break
                
                # 빈 입력 처리
                if not user_input:
                    print("⚠️  질문을 입력해주세요.")
                    continue
                
                logger.info(f"IN: main() - 사용자 입력: {user_input}")
                
                # 그래프 실행
                result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
                logger.info(f"OUT: main() - 그래프 실행 완료")
                
                # 결과 출력
                print("\n" + "=" * 50)
                print("🎯 멀티에이전트 응답")
                print("=" * 50)
                
                # 메시지 출력
                for message in result["messages"]:
                    if hasattr(message, 'name') and message.name:
                        print(f"👤 {message.name}: {message.content}")
                    else:
                        print(f"💬 {message.content}")
                
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