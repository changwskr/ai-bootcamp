# trymultiagentopenai.py - OpenAI 기반 멀티 에이전트 시스템

OpenAI API와 LangGraph를 사용한 멀티 에이전트 시스템입니다. API 할당량 문제를 해결하기 위한 더미 모드를 포함하고 있습니다.

## 🎯 주요 특징

### ✅ **이중 모드 지원**
- **실제 OpenAI 모드**: 실제 GPT 모델 사용
- **더미 모드**: API 키 없이 테스트 가능

### ✅ **할당량 문제 해결**
- API 할당량 초과 시 자동 더미 모드 전환
- 개발 및 테스트 환경에서 안정적 실행

### ✅ **완전한 LangChain 호환성**
- `BaseChatModel` 상속으로 표준 인터페이스 구현
- `create_react_agent`와 완전 호환

## 📋 파일 구조

```python
trymultiagentopenai.py
├── 환경 변수 설정 및 검증
├── LLM 초기화 (OpenAI 또는 더미)
├── 시스템 프롬프트 정의
├── 라우팅 스키마 (Router)
├── 상태 정의 (State)
├── 도구 구현 (Tools)
├── 감독자 노드 (Supervisor)
├── 워커 에이전트 노드들
├── 그래프 구성 및 컴파일
└── 실행 예시
```

## 🚀 빠른 시작

### 1. 기본 실행 (더미 모드)

```bash
# 환경변수 없이도 실행 가능
python trymultiagentopenai.py
```

### 2. OpenAI API 사용

```bash
# 환경변수 설정
export OPENAI_API_KEY="your-openai-api-key"

# 실행
python trymultiagentopenai.py
```

### 3. 모드 전환

```python
# 파일 내에서 모드 변경
USE_DUMMY_LLM = False  # OpenAI API 사용
USE_DUMMY_LLM = True   # 더미 모드 사용 (기본값)
```

## 🔧 핵심 컴포넌트

### 1. DummyLLM 클래스

```python
class DummyLLM(BaseChatModel):
    bound_tools: list = []
    
    @property
    def _llm_type(self) -> str:
        return "dummy"
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # 더미 응답 생성 로직
        return LLMResult(generations=[[ChatGeneration(message=AIMessage(content=response_content))]])
    
    def bind_tools(self, tools):
        self.bound_tools = tools
        return self
```

**특징:**
- LangChain의 `BaseChatModel` 완전 호환
- `create_react_agent`와 호환되는 `bind_tools` 메서드
- 구조화된 출력 지원

### 2. 감독자 노드 (Supervisor)

```python
def supervisor_node(state: State) -> Command[Literal["cafeteria", "schedule", "__end__"]]:
    """감독자 노드 (더미 모드)"""
    messages = state["messages"]
    last_message = messages[-1] if messages else HumanMessage(content="")
    
    # 메시지 소스 기반 라우팅
    if hasattr(last_message, 'name') and last_message.name == "cafeteria":
        goto = "schedule"
    elif hasattr(last_message, 'name') and last_message.name == "schedule":
        goto = "FINISH"
    # 키워드 기반 라우팅
    elif "식당" in content or "점심" in content:
        goto = "cafeteria"
    elif "일정" in content or "스케줄" in content:
        goto = "schedule"
    else:
        goto = "FINISH"
```

**라우팅 로직:**
1. **메시지 소스 확인**: 어느 에이전트에서 온 응답인지 판단
2. **키워드 분석**: 요청 내용에 따른 워커 선택
3. **순차 처리**: cafeteria → schedule → FINISH

### 3. 워커 에이전트들

#### Cafeteria Agent
```python
def cafeteria_node(state: State) -> Command[Literal["supervisor"]]:
    """구내식당 에이전트 노드 (더미 모드)"""
    # 요일별 식단 정보 제공
    if "월요일" in last_message.content:
        response = f"월요일 식단은 {get_cafeteria_menu('monday')}입니다."
    # ...
```

#### Schedule Agent
```python
def schedule_node(state: State) -> Command[Literal["supervisor"]]:
    """일정 관리 에이전트 노드 (더미 모드)"""
    # 사용자 일정 정보 제공
    schedule = get_schedule("사용자")
    response = f"현재 {schedule}"
```

## 🛠️ 구현된 도구들

### 1. get_cafeteria_menu()
```python
@tool("get_cafeteria_menu")
def get_cafeteria_menu(day: str = "") -> str:
    """Return cafeteria menu for a given day."""
    weekly = {
        "monday": "비빔밥 / 미역국 / 김치",
        "tuesday": "제육볶음 / 된장국 / 상추겉절이",
        # ...
    }
    return weekly.get(the_day, f"{the_day} 요일 식단 정보가 없습니다.")
```

### 2. get_schedule()
```python
@tool("get_schedule")
def get_schedule(user: str) -> str:
    """Return remaining schedules for the user today."""
    return f"{user}님의 남은 일정: 14:00 아키텍처 회의, 16:00 코드리뷰, 18:00 스탠드업."
```

## 🔄 실행 흐름

```
1. 초기화
   ├── 환경변수 검증
   ├── OpenAI API 연결 테스트
   └── LLM 초기화 (OpenAI 또는 더미)

2. 사용자 요청 처리
   ├── 감독자 분석: "식당 + 일정" 요청 감지
   ├── 라우팅: cafeteria로 전송
   └── cafeteria 응답: 월요일 식단 정보

3. 후속 처리
   ├── 감독자 분석: cafeteria 응답 감지
   ├── 라우팅: schedule로 전송
   └── schedule 응답: 일정 정보

4. 완료
   ├── 감독자 분석: schedule 응답 감지
   ├── 라우팅: FINISH로 전송
   └── 작업 완료
```

## 📊 실행 예시

### 입력
```
"오늘 구내식당 점심 뭐야? 그리고 내 남은 일정도 알려줘."
```

### 출력
```
[OpenAI Env]
  OPENAI_API_KEY = **********M6kA
[OpenAI API Test OK] 연결 성공
[LLM Mode] 더미 LLM 사용 (할당량 문제 해결)

[Supervisor] 분석 중: '오늘 구내식당 점심 뭐야? 그리고 내 남은 일정도 알려줘.'
[Supervisor] 초기 요청: 식당과 일정 둘 다 요청됨 -> cafeteria로 라우팅
[Supervisor] 다음 노드: cafeteria

[Cafeteria] 처리 중: '오늘 구내식당 점심 뭐야? 그리고 내 남은 일정도 알려줘.'
[Cafeteria] 응답: 오늘은 월요일이고, 월요일 식단은 비빔밥 / 미역국 / 김치입니다.

[Supervisor] 분석 중: '오늘은 월요일이고, 월요일 식단은 비빔밥 / 미역국 / 김치입니다.'
[Supervisor] cafeteria 응답 받음 -> schedule로 라우팅
[Supervisor] 다음 노드: schedule

[Schedule] 처리 중: '오늘은 월요일이고, 월요일 식단은 비빔밥 / 미역국 / 김치입니다.'
[Schedule] 응답: 현재 사용자님의 남은 일정: 14:00 아키텍처 회의, 16:00 코드리뷰, 18:00 스탠드업.

[Supervisor] 분석 중: '현재 사용자님의 남은 일정: 14:00 아키텍처 회의, 16:00 코드리뷰, 18:00 스탠드업.'
[Supervisor] schedule 응답 받음 -> 작업 완료
[Supervisor] 작업 완료

=== Conversation Trace ===
[None] 오늘 구내식당 점심 뭐야? 그리고 내 남은 일정도 알려줘.
[cafeteria] 오늘은 월요일이고, 월요일 식단은 비빔밥 / 미역국 / 김치입니다.
[schedule] 현재 사용자님의 남은 일정: 14:00 아키텍처 회의, 16:00 코드리뷰, 18:00 스탠드업.
```

## 🐛 문제 해결

### 1. API 할당량 초과
```
Error code: 429 - {'error': {'message': 'You exceeded your current quota...'}}
```
**해결책:**
- `USE_DUMMY_LLM = True`로 설정
- 더미 모드에서 테스트 진행

### 2. LangChain 호환성 에러
```
AttributeError: 'DummyLLM' object has no attribute 'bind_tools'
```
**해결책:**
- `DummyLLM` 클래스에 `bind_tools` 메서드 구현
- `BaseChatModel` 상속 확인

### 3. 무한 루프
```
GraphRecursionError: Recursion limit of 25 reached
```
**해결책:**
- 메시지 소스 기반 라우팅 로직 확인
- 각 에이전트가 한 번씩만 실행되도록 제어

## 🔧 커스터마이징

### 새로운 워커 추가

1. **도구 정의**:
```python
@tool("new_tool")
def new_tool(param: str) -> str:
    return "새로운 도구 결과"
```

2. **에이전트 노드 추가**:
```python
def new_agent_node(state: State) -> Command[Literal["supervisor"]]:
    messages = state["messages"]
    last_message = messages[-1] if messages else HumanMessage(content="")
    
    # 에이전트 로직 구현
    response = "새로운 에이전트 응답"
    
    return Command(
        update={"messages": [HumanMessage(content=response, name="new_agent")]},
        goto="supervisor",
    )
```

3. **그래프에 추가**:
```python
builder.add_node("new_agent", new_agent_node)
```

4. **감독자 로직 수정**:
```python
# supervisor_node 함수에 추가
elif hasattr(last_message, 'name') and last_message.name == "new_agent":
    goto = "FINISH"
elif "새로운키워드" in content:
    goto = "new_agent"
```

### 모델 변경

```python
# OpenAI 모델 변경
llm = ChatOpenAI(
    model="gpt-4o",  # 또는 "gpt-3.5-turbo", "gpt-4-turbo"
    temperature=0.0,
)
```

## 📈 성능 최적화

### 1. 로깅 최적화
- 개발 시: 상세 로그 활성화
- 프로덕션: 로그 레벨 조정

### 2. 메모리 관리
- 대화 히스토리 길이 제한
- 불필요한 메시지 정리

### 3. 에러 처리
- API 호출 재시도 로직
- 폴백 응답 구현

## 🔮 향후 개선 계획

1. **병렬 처리**: 여러 워커 동시 실행
2. **메모리 최적화**: 대화 상태 압축
3. **웹 인터페이스**: Streamlit 대시보드
4. **지속성**: 대화 상태 저장/복원
5. **모니터링**: 성능 메트릭 수집

## 📝 라이선스

이 파일은 교육 및 연구 목적으로 제작되었습니다.

---

**참고**: 이 구현은 LangGraph의 공식 문서와 예제를 기반으로 하며, OpenAI API 할당량 문제를 해결하기 위한 더미 모드를 포함합니다. 