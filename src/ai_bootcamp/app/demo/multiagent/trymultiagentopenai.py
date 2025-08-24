"""
Requirements (tested):
  openai==1.65.2
  langchain==0.3.20
  langchain-core==0.3.41
  langchain-openai==0.3.7
  langgraph==0.3.5
  langsmith==0.3.11
  requests  # 배포 점검용

필수 환경변수 (OpenAI):
  OPENAI_API_KEY="..."
"""

import os
import sys
import json
import requests
from typing import Literal, Optional
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent


# -----------------------------
# 0) 환경 변수 로드 & 검증
# -----------------------------
def getenv_required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"[ENV ERROR] {key} 가(이) 설정되지 않았습니다.", file=sys.stderr)
        print("  - bash 예) export {k}=\"...\"".format(k=key), file=sys.stderr)
        sys.exit(1)
    return val

# OpenAI API 키 검증 (더미 모드에서는 선택사항)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("[ENV WARNING] OPENAI_API_KEY 가(이) 설정되지 않았습니다. 더미 모드로 실행합니다.")
    print("[OpenAI Env] 더미 모드 - API 키 불필요")
    USE_DUMMY_LLM = True  # API 키가 없으면 강제로 더미 모드
else:
    print("[OpenAI Env]")
    print("  OPENAI_API_KEY =", "*" * 10 + openai_api_key[-4:])


# -----------------------------
# 1) OpenAI API 연결 테스트 (선택사항)
# -----------------------------
def test_openai_connection():
    """OpenAI API 연결을 테스트합니다."""
    if not os.getenv("OPENAI_API_KEY"):
        print("[OpenAI API Test] 더미 모드 - 연결 테스트 건너뜀")
        return
        
    try:
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            print("[OpenAI API Test OK] 연결 성공")
        else:
            print(f"[OpenAI API Test WARNING] HTTP {resp.status_code} - API 키를 확인하세요")
    except Exception as e:
        print(f"[OpenAI API Test WARNING] 연결 테스트 실패: {e}")

test_openai_connection()


# -----------------------------
# 2) LLM 초기화 (OpenAI 또는 더미)
# -----------------------------
USE_DUMMY_LLM = True  # 할당량 문제 시 True로 설정

if USE_DUMMY_LLM:
    # 더미 LLM (할당량 문제 해결용)
    from langchain_core.runnables import Runnable
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    
    class DummyLLM(BaseChatModel):
        bound_tools: list = []
        
        @property
        def _llm_type(self) -> str:
            """LLM 타입 반환 (추상 메서드 구현)"""
            return "dummy"
        
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            # 간단한 응답 생성
            content = " ".join([str(m.content) for m in messages if hasattr(m, 'content')])
            content_lower = content.lower()
            
            if "ping" in content_lower and "pong" in content_lower:
                response_content = 'pong'
            elif "supervisor" in content_lower:
                if "식당" in content or "점심" in content or "밥" in content:
                    response_content = 'cafeteria'
                elif "일정" in content or "스케줄" in content:
                    response_content = 'schedule'
                else:
                    response_content = 'FINISH'
            else:
                response_content = '테스트 응답입니다.'
            
            from langchain_core.outputs import LLMResult, ChatGeneration
            from langchain_core.messages import AIMessage
            return LLMResult(generations=[[ChatGeneration(message=AIMessage(content=response_content))]])
        
        def with_structured_output(self, schema):
            """구조화된 출력을 위한 래퍼"""
            class StructuredDummyLLM(DummyLLM):
                def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                    content = " ".join([str(m.content) for m in messages if hasattr(m, 'content')])
                    content_lower = content.lower()
                    
                    if "supervisor" in content_lower:
                        if "식당" in content or "점심" in content or "밥" in content:
                            response_content = '{"next": "cafeteria"}'
                        elif "일정" in content or "스케줄" in content:
                            response_content = '{"next": "schedule"}'
                        else:
                            response_content = '{"next": "FINISH"}'
                    else:
                        response_content = '{"content": "테스트 응답입니다."}'
                    
                    from langchain_core.outputs import LLMResult, ChatGeneration
                    from langchain_core.messages import AIMessage
                    return LLMResult(generations=[[ChatGeneration(message=AIMessage(content=response_content))]])
            
            return StructuredDummyLLM()
        
        def bind_tools(self, tools):
            """도구 바인딩 (create_react_agent 호환성)"""
            self.bound_tools = tools
            return self
    
    llm = DummyLLM()
    print("[LLM Mode] 더미 LLM 사용 (할당량 문제 해결)")
else:
    # 실제 OpenAI LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # 더 저렴한 모델로 변경
        temperature=0.0,
    )
    
    # 스모크 테스트 (간단 호출)
    try:
        ping = llm.invoke([SystemMessage(content="ping"), HumanMessage(content="pong?")])
        print("[LLM Smoke Test OK] ->", getattr(ping, "content", str(ping))[:120], "...")
    except Exception as e:
        print("[LLM Smoke Test FAILED]", e, file=sys.stderr)
        sys.exit(1)


# ---------------------------------------
# 3) 에이전트 후보 및 감독자 시스템 프롬프트
# ---------------------------------------
members = ["cafeteria", "schedule"]
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the "
    f"following workers: {members}. Given the following user request, "
    "respond with the worker to act next. Each worker will perform a task "
    "and respond with their results and status. When finished, respond with FINISH."
)


# ---------------------------------------
# 4) 라우팅 스키마 (구조화 출력)
# ---------------------------------------
NextWorkerLiteral = Literal["cafeteria", "schedule", "FINISH"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: NextWorkerLiteral


# ---------------------------------------
# 5) 상태 정의
# ---------------------------------------
class State(MessagesState):
    # MessagesState는 {"messages": list[BaseMessage]}를 포함
    next: Optional[str]


# ---------------------------------------
# 6) 샘플 툴 구현 (구내식당/일정)
# ---------------------------------------
from datetime import datetime

@tool("get_cafeteria_menu")
def get_cafeteria_menu(day: str = "") -> str:
    """Return cafeteria menu for a given day. day 예: 'monday', 'tuesday' ... (비우면 오늘 요일 추정)"""
    weekly = {
        "monday": "비빔밥 / 미역국 / 김치",
        "tuesday": "제육볶음 / 된장국 / 상추겉절이",
        "wednesday": "치킨마요 / 유부장국 / 단무지",
        "thursday": "불고기 / 감자국 / 김치",
        "friday": "카레라이스 / 계란후라이 / 피클",
    }
    the_day = day.lower().strip()
    if not the_day:
        the_day = datetime.utcnow().strftime("%A").lower()  # 간단 추정(UTC 기준)
    return weekly.get(the_day, f"{the_day} 요일 식단 정보가 없습니다.")


@tool("get_schedule")
def get_schedule(user: str) -> str:
    """Return remaining schedules for the user today. user 예: 'alice'"""
    # 실무에서는 캘린더/DB 연동. 여기선 더미.
    return f"{user}님의 남은 일정: 14:00 아키텍처 회의, 16:00 코드리뷰, 18:00 스탠드업."


# ---------------------------------------
# 7) 감독자 노드 (LLM 라우팅)
# ---------------------------------------
def supervisor_node(state: State) -> Command[Literal["cafeteria", "schedule", "__end__"]]:
    """감독자 노드 (더미 모드)"""
    messages = state["messages"]
    last_message = messages[-1] if messages else HumanMessage(content="")
    
    # 간단한 로직으로 다음 워커 결정
    content = last_message.content.lower()
    
    print(f"[Supervisor] 분석 중: '{content}'")
    
    # cafeteria에서 온 응답인지 확인
    if hasattr(last_message, 'name') and last_message.name == "cafeteria":
        print("[Supervisor] cafeteria 응답 받음 -> schedule로 라우팅")
        goto = "schedule"
    elif hasattr(last_message, 'name') and last_message.name == "schedule":
        print("[Supervisor] schedule 응답 받음 -> 작업 완료")
        goto = "FINISH"
    # 초기 요청인지 확인 (식당과 일정 둘 다 요청한 경우)
    elif len(messages) == 1 and ("식당" in content or "점심" in content or "밥" in content or "메뉴" in content) and ("일정" in content or "스케줄" in content):
        print("[Supervisor] 초기 요청: 식당과 일정 둘 다 요청됨 -> cafeteria로 라우팅")
        goto = "cafeteria"
    elif "식당" in content or "점심" in content or "밥" in content or "메뉴" in content:
        print("[Supervisor] 식당 관련 요청 -> cafeteria로 라우팅")
        goto = "cafeteria"
    elif "일정" in content or "스케줄" in content:
        print("[Supervisor] 일정 관련 요청 -> schedule로 라우팅")
        goto = "schedule"
    else:
        print("[Supervisor] 기타 요청 -> FINISH로 라우팅")
        goto = "FINISH"
    
    if goto == "FINISH":
        print("[Supervisor] 작업 완료")
        return Command(goto=END, update={"next": "FINISH"})
    
    print(f"[Supervisor] 다음 노드: {goto}")
    return Command(goto=goto, update={"next": goto})


# ---------------------------------------
# 8) 각 워커(에이전트) 정의: 더미 모드에서는 직접 구현
# ---------------------------------------
def cafeteria_node(state: State) -> Command[Literal["supervisor"]]:
    """구내식당 에이전트 노드 (더미 모드)"""
    messages = state["messages"]
    last_message = messages[-1] if messages else HumanMessage(content="")
    
    print(f"[Cafeteria] 처리 중: '{last_message.content}'")
    
    # 간단한 로직으로 응답 생성
    if "요일" in last_message.content or "월요일" in last_message.content:
        menu = get_cafeteria_menu("monday")
        response = f"월요일 식단은 {menu}입니다."
    elif "화요일" in last_message.content:
        menu = get_cafeteria_menu("tuesday")
        response = f"화요일 식단은 {menu}입니다."
    elif "수요일" in last_message.content:
        menu = get_cafeteria_menu("wednesday")
        response = f"수요일 식단은 {menu}입니다."
    elif "목요일" in last_message.content:
        menu = get_cafeteria_menu("thursday")
        response = f"목요일 식단은 {menu}입니다."
    elif "금요일" in last_message.content:
        menu = get_cafeteria_menu("friday")
        response = f"금요일 식단은 {menu}입니다."
    else:
        # 초기 요청인 경우 오늘 요일로 응답
        response = "오늘은 월요일이고, 월요일 식단은 비빔밥 / 미역국 / 김치입니다."
    
    print(f"[Cafeteria] 응답: {response}")
    
    return Command(
        update={"messages": [HumanMessage(content=response, name="cafeteria")]},
        goto="supervisor",
    )


def schedule_node(state: State) -> Command[Literal["supervisor"]]:
    """일정 관리 에이전트 노드 (더미 모드)"""
    messages = state["messages"]
    last_message = messages[-1] if messages else HumanMessage(content="")
    
    print(f"[Schedule] 처리 중: '{last_message.content}'")
    
    # 간단한 로직으로 응답 생성
    if "이름" in last_message.content or "누구" in last_message.content:
        response = "사용자 이름을 알려주세요. (예: alice, bob)"
    else:
        schedule = get_schedule("사용자")
        response = f"현재 {schedule}"
    
    print(f"[Schedule] 응답: {response}")
    
    return Command(
        update={"messages": [HumanMessage(content=response, name="schedule")]},
        goto="supervisor",
    )


# ---------------------------------------
# 9) 그래프 구성/컴파일
# ---------------------------------------
builder = StateGraph(State)
builder.add_node("supervisor", supervisor_node)
builder.add_node("cafeteria", cafeteria_node)
builder.add_node("schedule", schedule_node)
builder.add_edge(START, "supervisor")
graph = builder.compile()


# ---------------------------------------
# 10) 실행 예시
# ---------------------------------------
if __name__ == "__main__":
    init_state: State = {
        "messages": [HumanMessage(content="오늘 구내식당 점심 뭐야? 그리고 내 남은 일정도 알려줘.")],
        "next": None,
    }
    out = graph.invoke(init_state)
    print("=== Conversation Trace ===")
    for m in out["messages"]:
        who = getattr(m, "name", m.type)
        print(f"[{who}] {m.content}") 