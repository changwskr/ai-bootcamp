#!/usr/bin/env python3
"""
멀티에이전트 시스템 - 기업 정책 문서에서 액션아이템 도출 & 1페이지 요약 보고서
Supervisor가 5개 에이전트를 오케스트레이션하는 LangGraph 기반 시스템
"""

import logging
import json
import os
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock 모드 설정
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

# OpenAI 클라이언트 초기화
if not USE_MOCK:
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
else:
    llm = None

# ---------- 상태(전역 컨텍스트) ----------
class State(TypedDict, total=False):
    query: str                    # 사용자 질문
    docs: List[str]              # 검색된 근거 문단
    summary: str                 # 정책 10줄 요약
    actions: List[dict]          # [{team, action, due, type, evidence}]
    compliance: str              # 리스크/보완책
    report_ko: str               # 한국어 보고서
    report_en: str               # 영어 보고서
    needs_more_evidence: bool    # 근거 부족 플래그
    retry_count: int             # 재시도 횟수


# ---------- 각 노드(에이전트) ----------
def retriever_node(state: State) -> State:
    """1. Retriever 에이전트: 문서에서 근거 문단 검색(RAG)"""
    logger.info("IN: retriever_node() - 문서 검색 시작")
    
    try:
        # TODO: 실제 프로젝트에서는 VectorStore 질의로 교체
        # 현재는 시뮬레이션용 가짜 데이터
        fake_docs = [
            "제3조: 개인정보 암호화는 전 구간 의무. 민감정보는 AES-256 이상 적용.",
            "제5조: 접근통제는 RBAC로 최소권한 원칙 적용. 정기 권한 검토 필수.",
            "제7조: 로그는 1년 보관, 중요 시스템은 3년. 무결성 검증 포함.",
            "제9조: 외부 접속은 VPN 필수. 다중인증 적용.",
            "제11조: 데이터 백업은 일일 실시. 복구 테스트 분기별 수행."
        ]
        
        logger.info(f"OUT: retriever_node() - {len(fake_docs)}개 문서 검색 완료")
        return {
            "docs": fake_docs, 
            "needs_more_evidence": False,
            "retry_count": state.get("retry_count", 0) + 1
        }
    except Exception as e:
        logger.error(f"OUT: retriever_node() - 오류 발생: {e}")
        return {"docs": [], "needs_more_evidence": True}


def summarizer_node(state: State) -> State:
    """2. Summarizer 에이전트: 정책 핵심 10줄 요약"""
    logger.info("IN: summarizer_node() - 정책 요약 시작")
    
    try:
        docs = state.get("docs", [])
        if not docs:
            logger.warning("OUT: summarizer_node() - 검색된 문서 없음")
            return {"summary": "문서를 찾을 수 없습니다.", "needs_more_evidence": True}
        
        prompt = f"""다음 근거만으로 정책 핵심을 10줄 이내로 요약하라.
근거:
{chr(10).join(docs)}
추측 금지. 객관적 사실만 포함."""
        
        if USE_MOCK:
            # Mock 응답
            summary = f"""정책 핵심 요약 (Mock 모드):
1. 개인정보 암호화는 전 구간에서 의무적으로 적용되어야 함
2. 민감정보는 AES-256 이상의 암호화 알고리즘 사용 필수
3. 접근통제는 RBAC(Role-Based Access Control) 방식으로 구현
4. 최소권한 원칙을 적용하여 사용자 권한을 제한적으로 부여
5. 정기적인 권한 검토를 통해 불필요한 권한을 제거
6. 시스템 로그는 기본적으로 1년간 보관
7. 중요 시스템의 로그는 3년간 보관
8. 로그 무결성 검증을 통해 변조 여부를 확인
9. 외부 접속 시 VPN 사용을 의무화
10. 다중인증(MFA) 적용으로 보안 강화"""
        else:
            summary = llm.invoke(prompt).content
        
        # 간단 기준: 요약이 2줄 이하이면 근거 부족으로 재검색
        needs_more = len(summary.splitlines()) < 3
        
        logger.info(f"OUT: summarizer_node() - 요약 완료 (줄수: {len(summary.splitlines())})")
        return {"summary": summary, "needs_more_evidence": needs_more}
        
    except Exception as e:
        logger.error(f"OUT: summarizer_node() - 오류 발생: {e}")
        return {"summary": "요약 생성 중 오류가 발생했습니다.", "needs_more_evidence": True}


def action_node(state: State) -> State:
    """3. ActionMiner 에이전트: 부서별 액션아이템 도출"""
    logger.info("IN: action_node() - 액션아이템 도출 시작")
    
    try:
        summary = state.get("summary", "")
        docs = state.get("docs", [])
        
        if not summary or summary == "문서를 찾을 수 없습니다.":
            logger.warning("OUT: action_node() - 요약 정보 부족")
            return {"actions": []}
        
        prompt = f"""정책 요약을 바탕으로 부서별 액션아이템을 도출하라.

팀: 보안, 개발, 운영, 준법감시
SMART 규칙 적용: 구체적/측정가능/달성가능/현실적/기한설정

각 항목은 다음 형식으로 JSON 배열로만 출력:
[
  {{
    "team": "팀명",
    "action": "구체적 액션",
    "due": "YYYY-MM-DD",
    "type": "Policy/Process/Tech",
    "evidence": "근거조항"
  }}
]

요약:
{summary}

근거:
{chr(10).join(docs)}

최대 8개 액션아이템까지 생성하라."""

        if USE_MOCK:
            # Mock 응답
            actions_json = """[
  {
    "team": "보안",
    "action": "개인정보 암호화 적용 점검 및 AES-256 이상 알고리즘 적용",
    "due": "2025-09-30",
    "type": "Tech",
    "evidence": "제3조"
  },
  {
    "team": "운영",
    "action": "RBAC 기반 접근통제 시스템 구축 및 최소권한 원칙 적용",
    "due": "2025-08-31",
    "type": "Tech",
    "evidence": "제5조"
  },
  {
    "team": "운영",
    "action": "로그 보관 정책 수립 및 무결성 검증 시스템 구축",
    "due": "2025-10-15",
    "type": "Policy",
    "evidence": "제7조"
  },
  {
    "team": "보안",
    "action": "VPN 및 다중인증 시스템 구축",
    "due": "2025-11-30",
    "type": "Tech",
    "evidence": "제9조"
  },
  {
    "team": "준법감시",
    "action": "정기 권한 검토 프로세스 수립",
    "due": "2025-12-31",
    "type": "Process",
    "evidence": "제5조"
  }
]"""
        else:
            actions_json = llm.invoke(prompt).content
        
        # JSON 파싱 시도
        try:
            # JSON 블록 추출
            if "```json" in actions_json:
                actions_json = actions_json.split("```json")[1].split("```")[0]
            elif "```" in actions_json:
                actions_json = actions_json.split("```")[1]
            
            actions = json.loads(actions_json)
            logger.info(f"OUT: action_node() - {len(actions)}개 액션아이템 생성 완료")
            return {"actions": actions}
            
        except json.JSONDecodeError as e:
            logger.error(f"OUT: action_node() - JSON 파싱 오류: {e}")
            # 기본 액션아이템 반환
            default_actions = [
                {
                    "team": "보안",
                    "action": "개인정보 암호화 적용 점검",
                    "due": "2025-09-30",
                    "type": "Tech",
                    "evidence": "제3조"
                },
                {
                    "team": "운영",
                    "action": "로그 보관 정책 수립",
                    "due": "2025-08-31",
                    "type": "Policy",
                    "evidence": "제7조"
                }
            ]
            return {"actions": default_actions}
            
    except Exception as e:
        logger.error(f"OUT: action_node() - 오류 발생: {e}")
        return {"actions": []}


def compliance_node(state: State) -> State:
    """4. Compliance 에이전트: 규정 위반/리스크 및 보완책"""
    logger.info("IN: compliance_node() - 준수성 검토 시작")
    
    try:
        actions = state.get("actions", [])
        docs = state.get("docs", [])
        
        if not actions:
            logger.warning("OUT: compliance_node() - 액션아이템 없음")
            return {"compliance": "액션아이템이 없어 준수성 검토를 수행할 수 없습니다."}
        
        prompt = f"""액션아이템과 근거 간 충돌/위험을 점검하고 보완책을 제시하라.

간결하게 요약 보고서 섹션 형태로 작성:
1. 주요 리스크
2. 규정 준수 여부
3. 보완책 제안

액션아이템:
{json.dumps(actions, ensure_ascii=False, indent=2)}

근거:
{chr(10).join(docs)}

한국어로 작성하라."""

        if USE_MOCK:
            # Mock 응답
            compliance = """준수성 검토 결과 (Mock 모드):

1. 주요 리스크
- 개인정보 암호화 미적용 시 개인정보보호법 위반 위험
- 접근통제 미흡으로 인한 무단 접근 위험
- 로그 보관 미준수 시 증거 보존 실패 위험

2. 규정 준수 여부
- 제3조: 개인정보 암호화 의무 준수 필요
- 제5조: RBAC 기반 접근통제 구현 필요
- 제7조: 로그 보관 기간 준수 필요
- 제9조: VPN 및 다중인증 적용 필요

3. 보완책 제안
- 단계별 암호화 적용 계획 수립
- 접근통제 정책 및 절차 문서화
- 로그 관리 시스템 구축 및 모니터링
- 보안 교육 및 인식 제고 프로그램 운영"""
        else:
            compliance = llm.invoke(prompt).content
        
        logger.info("OUT: compliance_node() - 준수성 검토 완료")
        return {"compliance": compliance}
        
    except Exception as e:
        logger.error(f"OUT: compliance_node() - 오류 발생: {e}")
        return {"compliance": "준수성 검토 중 오류가 발생했습니다."}


def translate_node(state: State) -> State:
    """5. Translator 에이전트: 최종 1페이지 보고서를 다국어"""
    logger.info("IN: translate_node() - 번역 시작")
    
    try:
        summary = state.get("summary", "")
        actions = state.get("actions", [])
        compliance = state.get("compliance", "")
        
        # 한국어 보고서 생성
        actions_text = ""
        for i, action in enumerate(actions, 1):
            actions_text += f"{i}. [{action['team']}] {action['action']} (기한: {action['due']}, 유형: {action['type']})\n"
        
        report_ko = f"""[정책 요약]
{summary}

[액션아이템]
{actions_text}

[리스크 및 준수성 검토]
{compliance}

[근거 조항]
{chr(10).join(state.get('docs', []))}"""

        # 영어 번역
        if USE_MOCK:
            # Mock 영어 번역
            report_en = f"""Multi-Agent Analysis Report (Mock Mode)

[Policy Summary]
{summary}

[Action Items]
{actions_text}

[Risk and Compliance Review]
{compliance}

[Evidence Clauses]
{chr(10).join(state.get('docs', []))}"""
        else:
            translate_prompt = f"""Translate the following Korean business report to English. 
Maintain professional business report tone and format:

{report_ko}"""

            report_en = llm.invoke(translate_prompt).content
        
        logger.info("OUT: translate_node() - 번역 완료")
        return {"report_ko": report_ko, "report_en": report_en}
        
    except Exception as e:
        logger.error(f"OUT: translate_node() - 오류 발생: {e}")
        return {"report_ko": "보고서 생성 중 오류가 발생했습니다.", "report_en": "Error occurred during report generation."}


# ---------- 조건부 라우팅 함수 ----------
def cond_after_summary(state: State) -> str:
    """요약 후 조건부 라우팅: 근거 부족 시 재검색"""
    needs_more = state.get("needs_more_evidence", False)
    retry_count = state.get("retry_count", 0)
    
    if needs_more and retry_count < 3:  # 최대 3회 재시도
        logger.info(f"IN: cond_after_summary() - 재검색 필요 (재시도: {retry_count})")
        return "retriever"
    else:
        logger.info("IN: cond_after_summary() - 다음 단계 진행")
        return "action"


def main():
    """메인 함수"""
    logger.info("IN: main() - 멀티에이전트 시스템 시작")
    
    try:
        # ---------- 그래프 정의 ----------
        graph = StateGraph(State)
        
        # 노드 등록
        graph.add_node("retriever", retriever_node)
        graph.add_node("summarizer", summarizer_node)
        graph.add_node("action", action_node)
        graph.add_node("compliance", compliance_node)
        graph.add_node("translator", translate_node)
        
        # 기본 흐름
        graph.add_edge("retriever", "summarizer")
        
        # 조건 분기: 요약이 부실하면 재검색
        graph.add_conditional_edges("summarizer", cond_after_summary, {
            "retriever": "retriever",
            "action": "action"
        })
        
        graph.add_edge("action", "compliance")
        graph.add_edge("compliance", "translator")
        
        # 시작점 설정
        graph.set_entry_point("retriever")
        
        # 워크플로우 컴파일
        app = graph.compile()
        logger.info("OUT: main() - 워크플로우 컴파일 완료")
        
        print("=" * 80)
        print("🎯 멀티에이전트 시스템 - 기업 정책 문서 분석")
        print("=" * 80)
        print("💡 에이전트 구성:")
        print("   1. Retriever: 문서에서 근거 문단 검색")
        print("   2. Summarizer: 정책 핵심 10줄 요약")
        print("   3. ActionMiner: 부서별 액션아이템 도출")
        print("   4. Compliance: 규정 위반/리스크 및 보완책")
        print("   5. Translator: 최종 1페이지 보고서 다국어 생성")
        print("🔑 OpenAI API Key 필요: .env 파일에 OPENAI_API_KEY 설정")
        if USE_MOCK:
            print("🔄 Mock 모드 활성화: API 할당량 초과 시 테스트용")
        print("=" * 80)
        
        # 대화형 루프
        while True:
            try:
                # 사용자 입력 받기
                user_query = input("\n🤔 분석할 정책 주제를 입력하세요 (종료: END): ").strip()
                
                # END 입력 시 종료
                if user_query.upper() == "END":
                    logger.info("IN: main() - 사용자가 END를 입력하여 종료")
                    print("\n👋 멀티에이전트 시스템을 종료합니다. 감사합니다!")
                    break
                
                # 빈 입력 처리
                if not user_query:
                    print("⚠️  정책 주제를 입력해주세요.")
                    continue
                
                logger.info(f"IN: main() - 사용자 쿼리: {user_query}")
                
                # 워크플로우 실행
                result = app.invoke({"query": user_query})
                logger.info(f"OUT: main() - 워크플로우 실행 완료")
                
                # 결과 출력
                print("\n" + "=" * 60)
                print("🎯 멀티에이전트 분석 결과")
                print("=" * 60)
                
                print("\n📋 한국어 보고서:")
                print("-" * 40)
                print(result["report_ko"])
                
                print("\n📋 English Report:")
                print("-" * 40)
                print(result["report_en"])
                
                print("=" * 60)
                
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