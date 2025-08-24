#!/usr/bin/env python3
"""
LangGraph 예제 02
3개 노드를 3→2→1 순서로 실행하는 워크플로우 데모
"""

import logging
from typing import TypedDict
from langgraph.graph import StateGraph

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 상태 정의
class WorkflowState(TypedDict):
    input_data: str
    node3_result: str
    node2_result: str
    node1_result: str
    final_result: str


def main():
    """메인 함수"""
    logger.info("IN: main() - LangGraph 예제 02 시작")
    
    try:
        # 그래프 생성
        workflow = StateGraph(WorkflowState)
        
        # 노드 정의
        def node3_function(state):
            """3번 노드: 땡땡땡 출력"""
            logger.info("IN: node3_function() - 3번 노드 실행")
            result = "땡땡땡"
            logger.info(f"OUT: node3_function() - 3번 노드 완료: {result}")
            return {"node3_result": result}
        
        def node2_function(state):
            """2번 노드: 장우승 출력"""
            logger.info("IN: node2_function() - 2번 노드 실행")
            result = "장우승"
            logger.info(f"OUT: node2_function() - 2번 노드 완료: {result}")
            return {"node2_result": result}
        
        def node1_function(state):
            """1번 노드: 1+1 계산"""
            logger.info("IN: node1_function() - 1번 노드 실행")
            result = "1 + 1 = 2"
            logger.info(f"OUT: node1_function() - 1번 노드 완료: {result}")
            return {"node1_result": result}
        
        def final_node(state):
            """최종 결과 노드: 모든 결과 종합"""
            logger.info("IN: final_node() - 최종 결과 생성")
            final_result = f"최종 결과:\n- 3번 노드: {state['node3_result']}\n- 2번 노드: {state['node2_result']}\n- 1번 노드: {state['node1_result']}"
            logger.info(f"OUT: final_node() - 최종 결과 완료")
            return {"final_result": final_result}
        
        # 노드 등록
        workflow.add_node("node3", node3_function)
        workflow.add_node("node2", node2_function)
        workflow.add_node("node1", node1_function)
        workflow.add_node("final", final_node)
        
        # 연결 정의 (3→2→1→final 순서)
        workflow.add_edge("node3", "node2")
        workflow.add_edge("node2", "node1")
        workflow.add_edge("node1", "final")
        
        # 시작점 설정 (START에서 node3로)
        workflow.set_entry_point("node3")
        
        # 워크플로우 컴파일
        app = workflow.compile()
        logger.info("OUT: main() - 워크플로우 컴파일 완료")
        
        print("=" * 60)
        print("🎯 LangGraph 3→2→1 순서 워크플로우 데모")
        print("=" * 60)
        print("💡 워크플로우 순서:")
        print("   1. 3번 노드: 땡땡땡 출력")
        print("   2. 2번 노드: 장우승 출력")
        print("   3. 1번 노드: 1+1 계산")
        print("   4. 최종 노드: 결과 종합")
        print("=" * 60)
        
        # 대화형 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = input("\n🤔 시작하려면 아무 키나 누르세요 (종료: END): ").strip()
                
                # END 입력 시 종료
                if user_input.upper() == "END":
                    logger.info("IN: main() - 사용자가 END를 입력하여 종료")
                    print("\n👋 LangGraph 데모를 종료합니다. 감사합니다!")
                    break
                
                logger.info("IN: main() - 워크플로우 실행 시작")
                
                # 워크플로우 실행
                result = app.invoke({"input_data": user_input})
                logger.info(f"OUT: main() - 워크플로우 실행 완료")
                
                # 결과 출력
                print("\n" + "=" * 50)
                print("🎯 워크플로우 실행 결과")
                print("=" * 50)
                print(f"📝 입력 데이터: {result['input_data']}")
                print(f"🔢 3번 노드 결과: {result['node3_result']}")
                print(f"👤 2번 노드 결과: {result['node2_result']}")
                print(f"🧮 1번 노드 결과: {result['node1_result']}")
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