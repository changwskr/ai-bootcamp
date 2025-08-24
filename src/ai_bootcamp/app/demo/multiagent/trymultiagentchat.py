"""
Requirements (tested):
  openai==1.65.2
  langchain==0.3.20
  langchain-core==0.3.41
  langchain-openai==0.3.7
  langgraph==0.3.5
  langsmith==0.3.11
  requests  # 배포 점검용

필수 환경변수 (Azure OpenAI):
  AZURE_OPENAI_API_KEY="..."
  AZURE_OPENAI_ENDPOINT="https://<your-resource-name>.openai.azure.com"
  AZURE_OPENAI_API_VERSION="<ex: 2024-08-06 or 2024-10-21>"  # 배포 카드 권장값
  AZURE_OPENAI_DEPLOYMENT="<your-deployment-name>"           # '모델명'이 아니라 '배포명'
"""

import os
import sys
import json
import requests
from typing import Literal, Optional
from typing_extensions import TypedDict

from langchain_openai import AzureChatOpenAI
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

AZ_ENDPOINT   = getenv_required("AZURE_OPENAI_ENDPOINT").rstrip("/")
AZ_API_VER    = getenv_required("AZURE_OPENAI_API_VERSION")
AZ_DEPLOYMENT = getenv_required("AZURE_OPENAI_DEPLOYMENT")
# 키는 실제 호출에서만 사용
if not os.getenv("AZURE_OPENAI_API_KEY"):
    print("[ENV ERROR] AZURE_OPENAI_API_KEY 가(이) 설정되지 않았습니다.", file=sys.stderr)
    sys.exit(1)

print("[Azure OpenAI Env]")
print("  AZURE_OPENAI_ENDPOINT    =", AZ_ENDPOINT)
print("  AZURE_OPENAI_API_VERSION =", AZ_API_VER)
print("  AZURE_OPENAI_DEPLOYMENT  =", AZ_DEPLOYMENT)


# -----------------------------
# 1) 배포 목록 사전 점검 (필수)
# -----------------------------
def assert_deployment_exists(endpoint: str, api_version: str, api_key: str, deployment_name: str):
    url = f"{endpoint}/openai/deployments?api-version={api_version}"
    headers = {"api-key": api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[Preflight ERROR] deployments 조회 실패: HTTP {resp.status_code} -> {resp.text}", file=sys.stderr)
            sys.exit(1)
        data = resp.json()
    except Exception as e:
        print(f"[Preflight ERROR] deployments 조회 중 예외: {e}", file=sys.stderr)
        sys.exit(1)

    # 응답 형태 예: {"data":[{"id":"<deployment-name>", "model":"gpt-4o", ...}, ...]}
    names = [d.get("id") for d in data.get("data", []) if isinstance(d, dict)]
    print("[Preflight] 현재 리소스의 배포 목록:", names)
    if deployment_name not in names:
        print(
            f"[Preflight ERROR] 배포명이 존재하지 않습니다: '{deployment_name}'",
            file=sys.stderr
        )
        print("  - Azure AI Studio > Deployments 에서 배포명을 정확히 확인하세요.", file=sys.stderr)
        print("  - 배포 직후라면 수 분 뒤 다시 시도하세요.", file=sys.stderr)
        sys.exit(1)

assert_deployment_exists(
    endpoint=AZ_ENDPOINT,
    api_version=AZ_API_VER,
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    deployment_name=AZ_DEPLOYMENT,
)


# -----------------------------
# 2) LLM 초기화 (Azure OpenAI)
# -----------------------------
llm = AzureChatOpenAI(
    azure_deployment=AZ_DEPLOYMENT,
    api_version=AZ_API_VER,
    # endpoint는 SDK가 AZURE_OPENAI_ENDPOINT 환경변수로 읽습니다.
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
    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)] + state["messages"]
    response: Router = llm.with_structured_output(Router).invoke(messages)  # type: ignore
    goto = response["next"]
    if goto == "FINISH":
        return Command(goto=END, update={"next": "FINISH"})
    return Command(goto=goto, update={"next": goto})


# ---------------------------------------
# 8) 각 워커(에이전트) 정의: ReAct 프리빌트
# ---------------------------------------
cafeteria_agent = create_react_agent(
    model=llm,
    tools=[get_cafeteria_menu],
    prompt=(
        "당신은 구내식당을 관리하는 영양사입니다. 사용자에게 이번 주의 식단을 알려줄 수 있습니다. "
        "사용자가 요일을 말하지 않으면 먼저 오늘 요일을 물어보고 안내하세요."
    ),
)

def cafeteria_node(state: State) -> Command[Literal["supervisor"]]:
    result = cafeteria_agent.invoke(state)
    last = result["messages"][-1]
    return Command(
        update={"messages": [HumanMessage(content=last.content, name="cafeteria")]},
        goto="supervisor",
    )


schedule_agent = create_react_agent(
    model=llm,
    tools=[get_schedule],
    prompt=(
        "당신은 사용자의 일정을 관리하는 비서입니다. 사용자에게 현재 남아있는 일정을 안내합니다. "
        "사용자 이름이 없으면 먼저 사용자 이름을 물어보세요."
    ),
)

def schedule_node(state: State) -> Command[Literal["supervisor"]]:
    result = schedule_agent.invoke(state)
    last = result["messages"][-1]
    return Command(
        update={"messages": [HumanMessage(content=last.content, name="schedule")]},
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
