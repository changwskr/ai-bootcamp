from typing import Optional, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool

# --- 상태 정의 ---
print("[STATE] START - State 클래스 정의 시작")

class State(TypedDict, total=False):
    messages: list[str]
    next: Optional[str]

print(f"[STATE] State 클래스 정의 완료: {State}")
print(f"[STATE] State 필드: messages (list[str]), next (Optional[str])")
print(f"[STATE] total=False: 모든 필드가 선택적(optional)")
print("[STATE] END - State 클래스 정의 완료")

# --- Tool 함수들 ---
print("[TOOLS] START - Tool 함수 정의 시작")

@tool("router_tool")
def router_tool(input_text: str) -> str:
    """Router 노드에서 수행하는 도구 함수"""
    print("router working functioning")
    return "router working functioning"

@tool("cafeteria_tool")
def cafeteria_tool(input_text: str) -> str:
    """Cafeteria 노드에서 수행하는 도구 함수"""
    print("cafeteria working functioning")
    return "cafeteria working functioning"

print(f"[TOOLS] router_tool 정의: {router_tool}")
print(f"[TOOLS] cafeteria_tool 정의: {cafeteria_tool}")
print("[TOOLS] END - Tool 함수 정의 완료")

# --- 워커(노드)들 ---
def router(state: State) -> dict:
    """다음으로 보낼 워커를 결정"""
    print(f"[ROUTER] START - 입력 상태: {state}")
    
    # Router tool 호출
    print("[ROUTER] Router tool 호출 시작")
    router_result = router_tool.invoke("router_input")
    print(f"[ROUTER] Router tool 결과: {router_result}")
    
    text = (state.get("messages") or [""])[-1].lower()
    print(f"[ROUTER] 분석할 텍스트: '{text}'")
    
    if "점심" in text or "식당" in text:
        result = {"next": "cafeteria"}
        print(f"[ROUTER] 조건 만족 -> cafeteria로 라우팅")
    else:
        result = {"next": "FINISH"}  # 기본은 종료
        print(f"[ROUTER] 조건 불만족 -> FINISH로 라우팅")
    
    print(f"[ROUTER] END - 반환값: {result}")
    return result

def cafeteria(state: State) -> dict:
    """식당 메뉴 생성(샘플)"""
    print(f"[CAFETERIA] START - 입력 상태: {state}")
    
    # Cafeteria tool 호출
    print("[CAFETERIA] Cafeteria tool 호출 시작")
    cafeteria_result = cafeteria_tool.invoke("cafeteria_input")
    print(f"[CAFETERIA] Cafeteria tool 결과: {cafeteria_result}")
    
    msg = "오늘 구내식당: 비빔밥 / 미역국 / 김치"
    print(f"[CAFETERIA] 생성된 메시지: '{msg}'")
    
    msgs = (state.get("messages") or []) + [msg]
    print(f"[CAFETERIA] 업데이트된 메시지 목록: {msgs}")
    
    result = {"messages": msgs, "next": "FINISH"}
    print(f"[CAFETERIA] END - 반환값: {result}")
    return result

# --- 그래프 구성 ---
print("[GRAPH] START - 그래프 구성 시작")

wf = StateGraph(State)
print(f"[GRAPH] StateGraph 생성: {type(wf)}")

wf.add_node("router", router)
print("[GRAPH] router 노드 추가")

wf.add_node("cafeteria", cafeteria)
print("[GRAPH] cafeteria 노드 추가")

# 엔트리 지정
wf.add_edge(START, "router")
print(f"[GRAPH] START -> router 엣지 추가")

# router의 결과(next)로 분기
wf.add_conditional_edges(
    "router",
    lambda s: s.get("next", "FINISH"),
    {
        "cafeteria": "cafeteria",
        "FINISH": END
    }
)
print("[GRAPH] router 조건부 엣지 추가: cafeteria 또는 FINISH")

# cafeteria 끝나면 종료
wf.add_edge("cafeteria", END)
print("[GRAPH] cafeteria -> END 엣지 추가")

graph = wf.compile()
print("[GRAPH] 그래프 컴파일 완료")
print("[GRAPH] END - 그래프 구성 완료")

# --- 실행 ---
print("[EXECUTION] START - 실행 시작")

print("[STATE] State 객체 생성 시작")
init_state: State = {"messages": ["점심 뭐 먹지?"], "next": None}
print(f"[STATE] State 객체 생성 완료: {init_state}")
print(f"[STATE] State 객체 타입: {type(init_state)}")
print(f"[STATE] State 객체 키: {list(init_state.keys())}")
print(f"[STATE] State 객체 값: {list(init_state.values())}")
print("[STATE] State 객체 생성 완료")

print(f"[EXECUTION] 초기 상태: {init_state}")

print("[EXECUTION] 그래프 실행 중...")
final_state = graph.invoke(init_state)

print("[STATE] 최종 State 객체 분석")
print(f"[STATE] 최종 State 객체: {final_state}")
print(f"[STATE] 최종 State 객체 타입: {type(final_state)}")
print(f"[STATE] 최종 State 객체 키: {list(final_state.keys())}")
print(f"[STATE] 최종 State 객체 값: {list(final_state.values())}")
print(f"[STATE] messages 필드 길이: {len(final_state.get('messages', []))}")
print(f"[STATE] next 필드 값: {final_state.get('next')}")
print("[STATE] 최종 State 객체 분석 완료")

print(f"[EXECUTION] 최종 상태: {final_state}")

print("[EXECUTION] END - 실행 완료")
print(f"[RESULT] 최종 메시지: {final_state['messages'][-1]}")  # → 오늘 구내식당: 비빔밥 / 미역국 / 김치
