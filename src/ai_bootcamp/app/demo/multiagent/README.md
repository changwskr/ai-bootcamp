# 멀티 에이전트 시스템 (Multi-Agent System)

LangGraph를 사용한 멀티 에이전트 시스템 구현입니다. 감독자(Supervisor)와 워커(Worker) 에이전트들이 협력하여 사용자 요청을 처리합니다.

## 📁 파일 구조

```
multiagent/
├── README.md                           # 이 파일
├── trymultiagentchat.py               # Azure OpenAI 기반 멀티 에이전트
├── trymultiagentopenai.py             # OpenAI 기반 멀티 에이전트 (더미 모드 지원)
└── multiagent.py                      # 기본 멀티 에이전트 구현
```

## 🏗️ 시스템 아키텍처

### 감독자-워커 패턴 (Supervisor-Worker Pattern)

```
사용자 요청 → 감독자 → 워커1 → 감독자 → 워커2 → 감독자 → 완료
```

- **감독자 (Supervisor)**: 요청을 분석하고 적절한 워커에게 라우팅
- **워커 (Worker)**: 특정 작업을 수행하는 전문 에이전트

### 현재 구현된 워커들

1. **Cafeteria Agent**: 구내식당 메뉴 조회
2. **Schedule Agent**: 사용자 일정 관리

## 🚀 사용 방법

### 1. Azure OpenAI 사용 (trymultiagentchat.py)

```bash
# 환경변수 설정
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_VERSION="2024-10-21"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"

# 실행
python trymultiagentchat.py
```

### 2. OpenAI 사용 (trymultiagentopenai.py)

```bash
# 환경변수 설정
export OPENAI_API_KEY="your-openai-api-key"

# 실행
python trymultiagentopenai.py
```

### 3. 더미 모드 (API 키 불필요)

```python
# trymultiagentopenai.py에서
USE_DUMMY_LLM = True  # 기본값
```

## 🔧 주요 기능

### 1. 자동 라우팅
- 감독자가 요청 내용을 분석하여 적절한 워커 선택
- 키워드 기반 라우팅 (식당, 일정, 스케줄 등)

### 2. 도구 사용 (Tools)
- `get_cafeteria_menu()`: 요일별 식단 조회
- `get_schedule()`: 사용자 일정 조회

### 3. 상태 관리
- LangGraph의 `MessagesState`를 사용한 대화 상태 관리
- 메시지 히스토리 유지

### 4. 에러 처리
- API 할당량 초과 시 더미 모드로 자동 전환
- 무한 루프 방지 로직

## 📋 요구사항

### 필수 패키지
```bash
pip install langgraph langchain-openai langchain-core
```

### 권장 버전
```
openai==1.65.2
langchain==0.3.20
langchain-core==0.3.41
langchain-openai==0.3.7
langgraph==0.3.5
```

## 🎯 사용 예시

### 입력
```
"오늘 구내식당 점심 뭐야? 그리고 내 남은 일정도 알려줘."
```

### 출력
```
[Supervisor] 초기 요청: 식당과 일정 둘 다 요청됨 -> cafeteria로 라우팅
[Cafeteria] 응답: 오늘은 월요일이고, 월요일 식단은 비빔밥 / 미역국 / 김치입니다.
[Schedule] 응답: 현재 사용자님의 남은 일정: 14:00 아키텍처 회의, 16:00 코드리뷰, 18:00 스탠드업.
```

## 🔄 시스템 흐름

1. **초기화**: 환경변수 검증, LLM 초기화
2. **요청 분석**: 감독자가 사용자 요청 분석
3. **라우팅**: 적절한 워커 선택
4. **작업 수행**: 워커가 도구를 사용하여 작업 수행
5. **결과 반환**: 감독자에게 결과 전달
6. **완료**: 모든 작업 완료 시 종료

## 🛠️ 확장 방법

### 새로운 워커 추가

1. **도구 정의**:
```python
@tool("new_tool")
def new_tool(param: str) -> str:
    """새로운 도구 설명"""
    return "결과"
```

2. **에이전트 노드 추가**:
```python
def new_agent_node(state: State) -> Command[Literal["supervisor"]]:
    # 에이전트 로직 구현
    return Command(
        update={"messages": [HumanMessage(content=response, name="new_agent")]},
        goto="supervisor",
    )
```

3. **그래프에 노드 추가**:
```python
builder.add_node("new_agent", new_agent_node)
```

### 감독자 로직 수정

`supervisor_node` 함수에서 새로운 키워드와 라우팅 로직을 추가하면 됩니다.

## 🐛 문제 해결

### 1. API 할당량 초과
```
Error code: 429 - insufficient_quota
```
**해결**: 더미 모드 사용 (`USE_DUMMY_LLM = True`)

### 2. 환경변수 오류
```
[ENV ERROR] OPENAI_API_KEY 가(이) 설정되지 않았습니다.
```
**해결**: 환경변수 설정 또는 더미 모드 사용

### 3. 무한 루프
```
GraphRecursionError: Recursion limit of 25 reached
```
**해결**: 메시지 소스 기반 라우팅 로직 확인

## 📊 성능 모니터링

- **LLM 호출 횟수**: 더미 모드에서 추적
- **처리 시간**: 각 노드별 실행 시간
- **에러율**: API 호출 실패율

## 🔮 향후 개선 계획

1. **더 많은 워커 추가**: 이메일, 캘린더, 파일 관리 등
2. **메모리 관리**: 대화 히스토리 최적화
3. **병렬 처리**: 여러 워커 동시 실행
4. **웹 인터페이스**: Streamlit 대시보드
5. **지속성**: 대화 상태 저장 및 복원

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트, 기능 요청, 풀 리퀘스트를 환영합니다!

---

**참고**: 이 시스템은 LangGraph의 공식 문서와 예제를 기반으로 구현되었습니다. 