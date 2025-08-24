#!/usr/bin/env python3
"""
LangGraph 예제 03
1번, 2번 노드 동시 실행 → 2번 성공 시 3번 노드가 실행되는 조건부 워크플로우
"""

import logging
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 상태 정의
class WorkflowState(TypedDict):
    input_data: str
    node1_result: str
    node2_result: str
    node2_success: bool
    node3_result: str
    final_result: str


def main():
    """메인 함수"""
    logger.info("IN: main() - LangGraph 예제 03 시작")
    
    try:
        # 그래프 생성
        workflow = StateGraph(WorkflowState)
        
        # 노드 정의
        def node1_function(state):
            """1번 노드: 1+1 계산"""
            logger.info("IN: node1_function() - 1번 노드 실행")
            result = "1 + 1 = 2"
            logger.info(f"OUT: node1_function() - 1번 노드 완료: {result}")
            return {"node1_result": result}
        
        def node2_function(state):
            """2번 노드: 사용자 입력 TEXT 검증"""
            logger.info("IN: node2_function() - 2번 노드 실행")
            
            # 사용자로부터 TEXT 입력 받기
            print("\n📝 2번 노드: TEXT를 입력해주세요.")
            user_text = input("TEXT 입력: ").strip()
            
            # 입력 검증: "장우승"이면 성공, 아니면 실패
            if user_text == "장우승":
                result = f"성공: {user_text}"
                success = True
                logger.info(f"OUT: node2_function() - 2번 노드 성공: {result}")
            else:
                result = f"실패: '{user_text}'는 장우승이 아닙니다"
                success = False
                logger.info(f"OUT: node2_function() - 2번 노드 실패: {result}")
            
            return {
                "node2_result": result,
                "node2_success": success
            }
        
        def node3_function(state):
            """3번 노드: 땡땡땡 출력 (2번 노드 성공 시에만 실행)"""
            logger.info("IN: node3_function() - 3번 노드 실행")
            result = "땡땡땡"
            logger.info(f"OUT: node3_function() - 3번 노드 완료: {result}")
            return {"node3_result": result}
        
        def final_success_node(state):
            """성공 시 최종 결과 노드"""
            logger.info("IN: final_success_node() - 성공 시 최종 결과 생성")
            final_result = f"✅ 워크플로우 성공!\n- 1번 노드: {state['node1_result']}\n- 2번 노드: {state['node2_result']}\n- 3번 노드: {state['node3_result']}"
            logger.info("OUT: final_success_node() - 성공 시 최종 결과 완료")
            return {"final_result": final_result}
        
        def final_failure_node(state):
            """실패 시 최종 결과 노드"""
            logger.info("IN: final_failure_node() - 실패 시 최종 결과 생성")
            final_result = f"❌ 워크플로우 실패!\n- 1번 노드: {state['node1_result']}\n- 2번 노드: {state['node2_result']}\n- 3번 노드: 실행되지 않음 (2번 노드 실패)"
            logger.info("OUT: final_failure_node() - 실패 시 최종 결과 완료")
            return {"final_result": final_result}
        
        def route_to_node3(state):
            """2번 노드 성공 여부에 따라 3번 노드 또는 종료로 라우팅"""
            logger.info(f"IN: route_to_node3() - 2번 노드 성공 여부 확인: {state['node2_success']}")
            if state['node2_success']:
                logger.info("OUT: route_to_node3() - 3번 노드로 라우팅")
                return "node3"
            else:
                logger.info("OUT: route_to_node3() - 실패 노드로 라우팅")
                return "final_failure"
        
        # 노드 등록
        workflow.add_node("node1", node1_function)
        workflow.add_node("node2", node2_function)
        workflow.add_node("node3", node3_function)
        workflow.add_node("final_success", final_success_node)
        workflow.add_node("final_failure", final_failure_node)
        workflow.add_node("route_to_node3", route_to_node3)
        
        # 병렬 실행을 위한 조건부 엣지 설정
        workflow.add_conditional_edges(
            "node2",
            route_to_node3,
            {
                "node3": "node3",
                "final_failure": "final_failure"
            }
        )
        
        # 연결 정의
        workflow.add_edge("node1", "node2")  # 1번 → 2번
        workflow.add_edge("node3", "final_success")  # 3번 → 성공 최종
        
        # 시작점 설정 (START에서 node1로)
        workflow.set_entry_point("node1")
        
        # 워크플로우 컴파일
        app = workflow.compile()
        logger.info("OUT: main() - 워크플로우 컴파일 완료")
        
        print("=" * 70)
        print("🎯 LangGraph 조건부 워크플로우 데모")
        print("=" * 70)
        print("💡 워크플로우 순서:")
        print("   1. 1번 노드: 1+1 계산")
        print("   2. 2번 노드: 장우승 출력")
        print("   3. 조건 확인: 2번 노드 성공 여부")
        print("      - 성공 시: 3번 노드 실행 → 성공 결과")
        print("      - 실패 시: 실패 결과")
        print("💡 테스트 방법:")
        print("   - 성공 테스트: 2번 노드에서 '장우승' 입력")
        print("   - 실패 테스트: 2번 노드에서 다른 텍스트 입력")
        print("=" * 70)
        
        # 대화형 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = input("\n🤔 테스트할 텍스트를 입력하세요 (종료: END): ").strip()
                
                # END 입력 시 종료
                if user_input.upper() == "END":
                    logger.info("IN: main() - 사용자가 END를 입력하여 종료")
                    print("\n👋 LangGraph 데모를 종료합니다. 감사합니다!")
                    break
                
                # 빈 입력 처리
                if not user_input:
                    print("⚠️  텍스트를 입력해주세요.")
                    continue
                
                logger.info(f"IN: main() - 사용자 입력: {user_input}")
                
                # 워크플로우 실행
                result = app.invoke({"input_data": user_input})
                logger.info(f"OUT: main() - 워크플로우 실행 완료")
                
                # 결과 출력
                print("\n" + "=" * 50)
                print("🎯 워크플로우 실행 결과")
                print("=" * 50)
                print(f"📝 입력 데이터: {result['input_data']}")
                print(f"🧮 1번 노드 결과: {result['node1_result']}")
                print(f"👤 2번 노드 결과: {result['node2_result']}")
                print(f"✅ 2번 노드 성공 여부: {result['node2_success']}")
                
                if result['node2_success']:
                    print(f"🔢 3번 노드 결과: {result['node3_result']}")
                
                print("\n" + "=" * 30)
                print("📋 최종 결과:")
                print(result['final_result'])
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