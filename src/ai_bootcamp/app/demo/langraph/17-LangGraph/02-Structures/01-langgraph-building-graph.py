#!/usr/bin/env python3
"""
LangGraph 기본 그래프 생성 예제

이 스크립트는 LangGraph를 사용하여 그래프를 생성하는 방법을 보여줍니다.

LangGraph의 그래프를 정의하기 위해서는:
1. State 정의
2. 노드 정의
3. 그래프 정의
4. 그래프 컴파일
5. 그래프 시각화

단계를 거칩니다.

그래프 생성시 조건부 엣지를 사용하는 방법과 다양한 흐름 변경 방법을 알아봅니다.
"""

import operator
from typing import Annotated, Any, List, TypedDict

from langchain_core.documents import Document
from langgraph.graph import END, StateGraph

# LangSmith 추적 설정 (선택사항)
try:
    from langchain_teddynote.graphs import visualize_graph

    LANGCHAIN_TEDDYNOTE_AVAILABLE = True
except ImportError:
    print("LangSmith 추적을 사용하려면 'pip install langchain-teddynote'를 실행하세요.")
    LANGCHAIN_TEDDYNOTE_AVAILABLE = False

# Graphviz를 사용한 대안 시각화
try:
    import graphviz

    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Graphviz가 설치되지 않아 DOT 파일 생성이 불가능합니다.")

# PNG 생성을 위한 라이브러리
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    PNG_AVAILABLE = True
except ImportError:
    PNG_AVAILABLE = False
    print("matplotlib이 설치되지 않아 PNG 생성이 불가능합니다.")


def setup_environment():
    """환경 설정"""
    print("=== LangGraph 기본 그래프 생성 예제 ===")
    print("=" * 50)


def define_state():
    """State 정의"""
    print("\n=== 1. State 정의 ===")

    class GraphState(TypedDict):
        context: Annotated[List[Document], operator.add]
        answer: Annotated[List[Document], operator.add]
        question: Annotated[str, "user question"]
        sql_query: Annotated[str, "sql query"]
        binary_score: Annotated[str, "binary score yes or no"]

    print("GraphState 클래스가 정의되었습니다.")
    return GraphState


def define_nodes(GraphState):
    """노드 정의"""
    print("\n=== 2. 노드 정의 ===")

    def retrieve(state: GraphState) -> GraphState:
        """retrieve: 검색"""
        print("  - retrieve 노드 실행: 검색 수행")
        documents = [
            Document(page_content="검색된 문서", metadata={"source": "retrieve"})
        ]
        return {"context": documents}

    def rewrite_query(state: GraphState) -> GraphState:
        """Query Transform: 쿼리 재작성"""
        print("  - rewrite_query 노드 실행: 쿼리 재작성")
        documents = [
            Document(page_content="검색된 문서", metadata={"source": "rewrite_query"})
        ]
        return GraphState(context=documents)

    def llm_gpt_execute(state: GraphState) -> GraphState:
        """LLM 실행 (GPT)"""
        print("  - llm_gpt_execute 노드 실행: GPT 답변 생성")
        answer = [Document(page_content="GPT 생성된 답변", metadata={"source": "gpt"})]
        return GraphState(answer=answer)

    def llm_claude_execute(state: GraphState) -> GraphState:
        """LLM 실행 (Claude)"""
        print("  - llm_claude_execute 노드 실행: Claude 답변 생성")
        answer = [
            Document(page_content="Claude의 생성된 답변", metadata={"source": "claude"})
        ]
        return GraphState(answer=answer)

    def relevance_check(state: GraphState) -> GraphState:
        """Relevance Check: 관련성 확인"""
        print("  - relevance_check 노드 실행: 관련성 확인")
        binary_score = "Relevance Score"
        return GraphState(binary_score=binary_score)

    def sum_up(state: GraphState) -> GraphState:
        """sum_up: 결과 종합"""
        print("  - sum_up 노드 실행: 결과 종합")
        answer = [Document(page_content="종합된 답변", metadata={"source": "sum_up"})]
        return GraphState(answer=answer)

    def search_on_web(state: GraphState) -> GraphState:
        """Search on Web: 웹 검색"""
        print("  - search_on_web 노드 실행: 웹 검색")
        state_dict: dict[str, Any] = dict(state)
        existing_docs = state_dict.get("context", [])
        searched_documents = [
            Document(page_content="검색된 문서", metadata={"source": "web_search"})
        ]
        documents = existing_docs + searched_documents
        return GraphState(context=documents)

    def get_table_info(state: GraphState) -> GraphState:
        """Get Table Info: 테이블 정보 가져오기"""
        print("  - get_table_info 노드 실행: 테이블 정보 가져오기")
        table_info = [
            Document(page_content="테이블 정보", metadata={"source": "table_info"})
        ]
        return GraphState(context=table_info)

    def generate_sql_query(state: GraphState) -> GraphState:
        """Make SQL Query: SQL 쿼리 생성"""
        print("  - generate_sql_query 노드 실행: SQL 쿼리 생성")
        sql_query = "SQL 쿼리"
        return GraphState(sql_query=sql_query)

    def execute_sql_query(state: GraphState) -> GraphState:
        """Execute SQL Query: SQL 쿼리 실행"""
        print("  - execute_sql_query 노드 실행: SQL 쿼리 실행")
        sql_result = [
            Document(page_content="SQL 결과", metadata={"source": "sql_execution"})
        ]
        return GraphState(context=sql_result)

    def validate_sql_query(state: GraphState) -> GraphState:
        """Validate SQL Query: SQL 쿼리 검증"""
        print("  - validate_sql_query 노드 실행: SQL 쿼리 검증")
        binary_score = "SQL 쿼리 검증 결과"
        return GraphState(binary_score=binary_score)

    def handle_error(state: GraphState) -> GraphState:
        """Error Handling: 에러 처리"""
        print("  - handle_error 노드 실행: 에러 처리")
        error = [
            Document(page_content="에러 발생", metadata={"source": "error_handling"})
        ]
        return GraphState(context=error)

    def decision(state: GraphState) -> str:
        """의사결정"""
        print("  - decision 노드 실행: 의사결정")
        # 로직을 추가할 수 있습니다.

        state_dict: dict[str, Any] = dict(state)
        binary_score = state_dict.get("binary_score", "")
        if binary_score == "yes":
            return "종료"
        else:
            return "재검색"

    def sql_decision(state: GraphState) -> str:
        """SQL 의사결정"""
        print("  - sql_decision 노드 실행: SQL 의사결정")

        # SQL 검증 결과에 따른 분기
        state_dict: dict[str, Any] = dict(state)
        binary_score = state_dict.get("binary_score", "")
        if binary_score == "SQL 쿼리 검증 결과":
            return "PASS"  # 검증 통과
        elif "ERROR" in binary_score:
            return "QUERY ERROR"  # 쿼리 오류
        else:
            return "UNKNOWN MEANING"  # 의미 불명

    print("모든 노드 함수가 정의되었습니다.")
    return {
        "retrieve": retrieve,
        "rewrite_query": rewrite_query,
        "llm_gpt_execute": llm_gpt_execute,
        "llm_claude_execute": llm_claude_execute,
        "relevance_check": relevance_check,
        "sum_up": sum_up,
        "search_on_web": search_on_web,
        "get_table_info": get_table_info,
        "generate_sql_query": generate_sql_query,
        "execute_sql_query": execute_sql_query,
        "validate_sql_query": validate_sql_query,
        "handle_error": handle_error,
        "decision": decision,
        "sql_decision": sql_decision,
    }


def create_basic_rag_graph(GraphState, nodes):
    """기본 RAG 그래프 생성"""
    print("\n=== 3. 기본 RAG 그래프 정의 ===")

    # langgraph.graph에서 StateGraph와 END를 가져옵니다.
    workflow = StateGraph(GraphState)

    # 노드를 추가합니다.
    workflow.add_node("retrieve", nodes["retrieve"])
    # workflow.add_node("rewrite_query", nodes["rewrite_query"])  # (4)

    workflow.add_node("GPT 요청", nodes["llm_gpt_execute"])
    # workflow.add_node("Claude 요청", nodes["llm_claude_execute"])  # (3)
    workflow.add_node("GPT_relevance_check", nodes["relevance_check"])
    # workflow.add_node("Claude_relevance_check", nodes["relevance_check"])  # (3)
    workflow.add_node("결과 종합", nodes["sum_up"])

    # 각 노드들을 연결합니다.
    workflow.add_edge("retrieve", "GPT 요청")
    # workflow.add_edge("retrieve", "Claude 요청")  # (3)
    # workflow.add_edge("rewrite_query", "retrieve")  # (4)
    workflow.add_edge("GPT 요청", "GPT_relevance_check")
    workflow.add_edge("GPT_relevance_check", "결과 종합")
    # workflow.add_edge("Claude 요청", "Claude_relevance_check")  # (3)
    # workflow.add_edge("Claude_relevance_check", "결과 종합")  # (3)

    workflow.add_edge("결과 종합", END)  # (2) - off

    # 조건부 엣지를 추가합니다. (2), (4)
    # workflow.add_conditional_edges(
    #     "결과 종합",  # 관련성 체크 노드에서 나온 결과를 is_relevant 함수에 전달합니다.
    #     nodes["decision"],
    #     {
    #         "재검색": "retrieve",  # 관련성이 있으면 종료합니다.
    #         "종료": END,  # 관련성 체크 결과가 모호하다면 다시 답변을 생성합니다.
    #     },
    # )

    # 조건부 엣지를 추가합니다. (4)
    # workflow.add_conditional_edges(
    #     "결과 종합",  # 관련성 체크 노드에서 나온 결과를 is_relevant 함수에 전달합니다.
    #     nodes["decision"],
    #     {
    #         "재검색": "rewrite_query",  # 관련성이 있으면 종료합니다.
    #         "종료": END,  # 관련성 체크 결과가 모호하다면 다시 답변을 생성합니다.
    #     },
    # )

    # 시작점을 설정합니다.
    workflow.set_entry_point("retrieve")

    # 그래프를 컴파일합니다. (메모리 저장소 없이)
    app = workflow.compile()

    print("기본 RAG 그래프가 생성되었습니다.")
    return app


def create_sql_rag_graph(GraphState, nodes):
    """SQL RAG 그래프 생성"""
    print("\n=== 4. SQL RAG 그래프 정의 ===")

    # langgraph.graph에서 StateGraph와 END를 가져옵니다.
    workflow = StateGraph(GraphState)

    # 노드를 추가합니다.
    workflow.add_node("질문", nodes["retrieve"])
    workflow.add_node("rewrite_query", nodes["rewrite_query"])
    workflow.add_node("rewrite_question", nodes["rewrite_query"])
    workflow.add_node("GPT 요청", nodes["llm_gpt_execute"])
    workflow.add_node("GPT_relevance_check", nodes["relevance_check"])
    workflow.add_node("결과 종합", nodes["sum_up"])
    workflow.add_node("get_table_info", nodes["get_table_info"])
    workflow.add_node("generate_sql_query", nodes["generate_sql_query"])
    workflow.add_node("execute_sql_query", nodes["execute_sql_query"])
    workflow.add_node("validate_sql_query", nodes["validate_sql_query"])

    # 각 노드들을 연결합니다.
    workflow.add_edge("질문", "get_table_info")
    workflow.add_edge("get_table_info", "generate_sql_query")
    workflow.add_edge("generate_sql_query", "execute_sql_query")
    workflow.add_edge("execute_sql_query", "validate_sql_query")

    workflow.add_conditional_edges(
        "validate_sql_query",
        nodes["sql_decision"],
        {
            "QUERY ERROR": "rewrite_query",
            "UNKNOWN MEANING": "rewrite_question",
            "PASS": "GPT 요청",
        },
    )

    workflow.add_edge("rewrite_query", "execute_sql_query")
    workflow.add_edge("rewrite_question", "rewrite_query")
    workflow.add_edge("GPT 요청", "GPT_relevance_check")
    workflow.add_edge("GPT_relevance_check", "결과 종합")
    workflow.add_edge("결과 종합", END)

    # 시작점을 설정합니다.
    workflow.set_entry_point("질문")

    # 그래프를 컴파일합니다. (메모리 저장소 없이)
    app = workflow.compile()

    print("SQL RAG 그래프가 생성되었습니다.")
    return app


def visualize_graphs(basic_app, sql_app):
    """그래프 시각화"""
    print("\n=== 5. 그래프 시각화 ===")

    if not LANGCHAIN_TEDDYNOTE_AVAILABLE:
        print("LangChain Teddynote가 설치되지 않아 고급 그래프 시각화를 건너뜁니다.")
        return

    try:
        print("기본 RAG 그래프 시각화:")
        visualize_graph(basic_app)

        print("\nSQL RAG 그래프 시각화:")
        visualize_graph(sql_app)
    except Exception as e:
        print(f"그래프 시각화 중 오류 발생: {e}")


def visualize_graph_detailed(app, graph_name="Graph"):
    """상세한 그래프 시각화"""
    print(f"\n=== {graph_name} 상세 시각화 ===")

    if not LANGCHAIN_TEDDYNOTE_AVAILABLE:
        print("LangChain Teddynote가 설치되지 않아 고급 그래프 시각화를 건너뜁니다.")
        return

    try:
        # 기본 시각화
        print(f"{graph_name} 기본 시각화:")
        visualize_graph(app)

        # 그래프 정보 출력
        nodes = list(app.nodes.keys()) if hasattr(app, "nodes") else []
        entry_point = app.entry_point if hasattr(app, "entry_point") else "Unknown"

        print(f"\n{graph_name} 정보:")
        print(f"  - 노드 수: {len(nodes)}")
        print(f"  - 시작 노드: {entry_point}")

        # 노드 목록 출력
        print(f"\n{graph_name} 노드 목록:")
        for node_name in nodes:
            print(f"  - {node_name}")

    except Exception as e:
        print(f"그래프 시각화 중 오류 발생: {e}")


def visualize_graph_comparison(graphs_dict):
    """여러 그래프 비교 시각화"""
    print("\n=== 그래프 비교 시각화 ===")

    if not LANGCHAIN_TEDDYNOTE_AVAILABLE:
        print("LangChain Teddynote가 설치되지 않아 고급 그래프 시각화를 건너뜁니다.")
        return

    try:
        for graph_name, app in graphs_dict.items():
            print(f"\n--- {graph_name} ---")
            visualize_graph(app)

            # 그래프 통계
            nodes = list(app.nodes.keys()) if hasattr(app, "nodes") else []
            print(f"  노드 수: {len(nodes)}")

    except Exception as e:
        print(f"그래프 비교 시각화 중 오류 발생: {e}")


def create_graph_summary(app, graph_name="Graph"):
    """그래프 요약 정보 생성"""
    print(f"\n=== {graph_name} 요약 정보 ===")

    try:
        # 그래프 객체의 속성 확인
        nodes = list(app.nodes.keys()) if hasattr(app, "nodes") else []
        entry_point = app.entry_point if hasattr(app, "entry_point") else "Unknown"

        # 엣지 정보는 다르게 접근
        edge_count = 0
        if hasattr(app, "graph") and hasattr(app.graph, "edges"):
            edge_count = len(app.graph.edges)
        elif hasattr(app, "graph") and hasattr(app.graph, "_edges"):
            edge_count = len(app.graph._edges)

        summary = {
            "name": graph_name,
            "nodes": nodes,
            "entry_point": entry_point,
            "node_count": len(nodes),
            "edge_count": edge_count,
        }

        print(f"그래프 이름: {summary['name']}")
        print(f"노드 수: {summary['node_count']}")
        print(f"엣지 수: {summary['edge_count']}")
        print(f"시작 노드: {summary['entry_point']}")
        print(f"노드 목록: {summary['nodes']}")

        return summary

    except Exception as e:
        print(f"그래프 요약 정보 생성 중 오류 발생: {e}")
        return {
            "name": graph_name,
            "nodes": [],
            "entry_point": "Unknown",
            "node_count": 0,
            "edge_count": 0,
        }


def visualize_graph_execution_flow(app, graph_name="Graph"):
    """그래프 실행 흐름 시각화"""
    print(f"\n=== {graph_name} 실행 흐름 ===")

    try:
        # 실행 흐름 시각화
        print(f"{graph_name}의 실행 흐름:")

        # 시작점부터 엔드포인트까지의 경로 추적
        entry_point = app.entry_point if hasattr(app, "entry_point") else "Unknown"
        path = [entry_point]

        print(f"  시작: {entry_point}")

        # 노드 목록을 기반으로 간단한 경로 추적
        nodes = list(app.nodes.keys()) if hasattr(app, "nodes") else []

        # 기본 RAG 그래프의 경우
        if "retrieve" in nodes and "GPT 요청" in nodes:
            path = ["retrieve", "GPT 요청", "GPT_relevance_check", "결과 종합"]
        # SQL RAG 그래프의 경우
        elif "질문" in nodes and "get_table_info" in nodes:
            path = [
                "질문",
                "get_table_info",
                "generate_sql_query",
                "execute_sql_query",
                "validate_sql_query",
                "GPT 요청",
                "GPT_relevance_check",
                "결과 종합",
            ]

        for node in path:
            print(f"  → {node}")

        print("  → END")
        print(f"  실행 경로: {' → '.join(path)} → END")

    except Exception as e:
        print(f"실행 흐름 시각화 중 오류 발생: {e}")


def export_graph_to_dot(app, graph_name="Graph", filename=None):
    """그래프를 DOT 형식으로 내보내기"""
    # 스크립트 실행 위치 기준으로 graph 디렉토리 경로 설정
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_dir = os.path.join(script_dir, "graph")

    if filename is None:
        filename = os.path.join(
            graph_dir, f"{graph_name.lower().replace(' ', '_')}.dot"
        )
    elif not os.path.isabs(filename):
        filename = os.path.join(graph_dir, filename)

    # graph 디렉토리 존재 여부 체크 및 생성
    if not os.path.exists(graph_dir):
        print(f"graph 디렉토리가 존재하지 않습니다. 생성합니다: {graph_dir}")
        os.makedirs(graph_dir, exist_ok=True)
        print("graph 디렉토리가 생성되었습니다.")
    else:
        print(f"graph 디렉토리가 이미 존재합니다: {graph_dir}")

    print(f"\n=== {graph_name} DOT 형식 내보내기 ===")
    print(f"파일명: {filename}")

    if not GRAPHVIZ_AVAILABLE:
        print("Graphviz가 설치되지 않아 DOT 파일 생성을 건너뜁니다.")
        return None

    try:
        # Graphviz 객체 생성
        dot = graphviz.Digraph(comment=f"{graph_name} Visualization")
        dot.attr(rankdir="LR")
        dot.attr("node", shape="box", style="filled", fillcolor="lightblue")
        dot.attr("edge", color="gray")

        # 노드 추가
        nodes = list(app.nodes.keys()) if hasattr(app, "nodes") else []
        entry_point = app.entry_point if hasattr(app, "entry_point") else None

        for node_name in nodes:
            if node_name == entry_point:
                dot.node(node_name, node_name, fillcolor="yellow")
            else:
                dot.node(node_name, node_name)

        # 엣지 추가 (그래프 타입에 따라 미리 정의된 엣지 사용)
        # 기본 RAG 그래프의 경우
        if "retrieve" in nodes and "llm_gpt_execute" in nodes:
            edges = [
                ("retrieve", "llm_gpt_execute"),
                ("llm_gpt_execute", "relevance_check"),
                ("relevance_check", "sum_up"),
            ]
        # SQL RAG 그래프의 경우
        elif "get_table_info" in nodes and "execute_sql_query" in nodes:
            edges = [
                ("get_table_info", "generate_sql_query"),
                ("generate_sql_query", "execute_sql_query"),
                ("execute_sql_query", "validate_sql_query"),
                ("validate_sql_query", "sql_decision"),
            ]
        else:
            edges = []

        for source, target in edges:
            dot.edge(source, target)

        # DOT 파일만 저장 (PNG 변환은 Graphviz 실행 파일이 필요)
        dot_content = dot.source
        with open(filename, "w", encoding="utf-8") as f:
            f.write(dot_content)

        print(f"Graphviz DOT 파일이 생성되었습니다: {filename}")
        print("PNG 변환을 위해서는 Graphviz 실행 파일이 필요합니다.")
        print("온라인 도구를 사용하여 시각화할 수 있습니다:")
        print("  - https://dreampuf.github.io/GraphvizOnline/")
        print("  - https://graphviz.org/Gallery/directed/")

        return filename

    except Exception as e:
        print(f"DOT 파일 생성 중 오류 발생: {e}")
        return None


def create_graph_png(app, graph_name="Graph", filename=None):
    """그래프를 PNG 이미지로 생성"""
    # 스크립트 실행 위치 기준으로 graph 디렉토리 경로 설정
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_dir = os.path.join(script_dir, "graph")

    if filename is None:
        filename = os.path.join(
            graph_dir, f"{graph_name.lower().replace(' ', '_')}.png"
        )
    elif not os.path.isabs(filename):
        filename = os.path.join(graph_dir, filename)

    # graph 디렉토리 존재 여부 체크 및 생성
    if not os.path.exists(graph_dir):
        print(f"graph 디렉토리가 존재하지 않습니다. 생성합니다: {graph_dir}")
        os.makedirs(graph_dir, exist_ok=True)
        print("graph 디렉토리가 생성되었습니다.")
    else:
        print(f"graph 디렉토리가 이미 존재합니다: {graph_dir}")

    print(f"\n=== {graph_name} PNG 이미지 생성 ===")
    print(f"파일명: {filename}")

    if not PNG_AVAILABLE:
        print("matplotlib 또는 pydot이 설치되지 않아 PNG 생성을 건너뜁니다.")
        return None

    try:
        # 그래프 정보 가져오기
        nodes = list(app.nodes.keys()) if hasattr(app, "nodes") else []
        entry_point = app.entry_point if hasattr(app, "entry_point") else None

        # matplotlib을 사용한 그래프 시각화
        # 한글 폰트 설정 - 시스템에서 사용 가능한 폰트만 사용
        import matplotlib.font_manager as fm

        # 시스템에서 사용 가능한 폰트 확인
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        # 한글 폰트 우선순위 설정
        korean_fonts = [
            "Malgun Gothic",  # Windows 기본 한글 폰트
            "NanumGothic",  # 나눔고딕
            "NanumBarunGothic",  # 나눔바른고딕
            "Dotum",  # 돋움
            "Gulim",  # 굴림
            "Batang",  # 바탕
            "SimHei",  # 중국어 폰트 (한글 지원)
            "Microsoft YaHei",  # 마이크로소프트 야헤이
        ]

        # 사용 가능한 한글 폰트 찾기
        selected_font = None
        for font in korean_fonts:
            if font in available_fonts:
                selected_font = font
                break

        if selected_font:
            plt.rcParams["font.family"] = [selected_font, "DejaVu Sans", "Arial"]
            print(f"한글 폰트 '{selected_font}'를 사용합니다.")
        else:
            # 한글 폰트가 없으면 기본 폰트 사용
            plt.rcParams["font.family"] = ["DejaVu Sans", "Arial"]
            print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")

        plt.rcParams["axes.unicode_minus"] = False

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect("equal")

        # 노드 위치 계산
        node_positions = {}
        if len(nodes) > 0:
            # 원형 배치
            import math

            center_x, center_y = 5, 5
            radius = 3

            for i, node in enumerate(nodes):
                if node == "__start__":
                    # 시작 노드는 중앙에 배치
                    node_positions[node] = (center_x, center_y)
                else:
                    # 다른 노드들은 원형으로 배치
                    angle = 2 * math.pi * i / len(nodes)
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    node_positions[node] = (x, y)

        # 노드 그리기
        for node, (x, y) in node_positions.items():
            if node == entry_point or node == "__start__":
                # 시작 노드는 노란색으로 강조
                color = "yellow"
                edgecolor = "orange"
                linewidth = 2
            else:
                color = "lightblue"
                edgecolor = "blue"
                linewidth = 1

            # 노드 박스 그리기
            box = FancyBboxPatch(
                (x - 0.8, y - 0.3),
                1.6,
                0.6,
                boxstyle="round,pad=0.1",
                facecolor=color,
                edgecolor=edgecolor,
                linewidth=linewidth,
            )
            ax.add_patch(box)

            # 노드 텍스트
            ax.text(
                x,
                y,
                node,
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                wrap=True,
            )

        # 엣지 그리기 (간단한 연결)
        if len(nodes) > 1:
            # 기본 RAG 그래프의 경우
            if "retrieve" in nodes and "llm_gpt_execute" in nodes:
                edges = [
                    ("retrieve", "llm_gpt_execute"),
                    ("llm_gpt_execute", "relevance_check"),
                    ("relevance_check", "sum_up"),
                ]
            # SQL RAG 그래프의 경우
            elif "get_table_info" in nodes and "execute_sql_query" in nodes:
                edges = [
                    ("get_table_info", "generate_sql_query"),
                    ("generate_sql_query", "execute_sql_query"),
                    ("execute_sql_query", "validate_sql_query"),
                    ("validate_sql_query", "sql_decision"),
                ]
            else:
                # 기본 연결 (순차적)
                edges = []
                for i in range(len(nodes) - 1):
                    if nodes[i] in node_positions and nodes[i + 1] in node_positions:
                        edges.append((nodes[i], nodes[i + 1]))

            # 엣지 그리기
            for source, target in edges:
                if source in node_positions and target in node_positions:
                    x1, y1 = node_positions[source]
                    x2, y2 = node_positions[target]

                    # 화살표 그리기
                    ax.annotate(
                        "",
                        xy=(x2, y2),
                        xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", color="gray", lw=1.5),
                    )

        # 그래프 제목
        ax.set_title(f"{graph_name} 구조", fontsize=16, fontweight="bold", pad=20)
        ax.axis("off")

        # PNG 파일로 저장
        plt.tight_layout()
        plt.savefig(
            filename, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none"
        )
        plt.close()

        print(f"PNG 이미지가 생성되었습니다: {filename}")

        return filename

    except Exception as e:
        print(f"PNG 생성 중 오류 발생: {e}")
        return None


def run_graph_example(app, initial_state):
    """그래프 실행 예제"""
    print("\n=== 6. 그래프 실행 예제 ===")

    try:
        # 그래프 실행 (메모리 저장소 없이)
        result = app.invoke(initial_state)
        print("그래프 실행 결과:")

        # Context 출력 (Document 리스트)
        context = result.get("context", [])
        if context:
            print(f"  - Context: {[doc.page_content for doc in context]}")
        else:
            print("  - Context: N/A")

        # Answer 출력 (Document 리스트)
        answer = result.get("answer", [])
        if answer:
            print(f"  - Answer: {[doc.page_content for doc in answer]}")
        else:
            print("  - Answer: N/A")

        print(f"  - Binary Score: {result.get('binary_score', 'N/A')}")
        return result
    except Exception as e:
        print(f"그래프 실행 중 오류 발생: {e}")
        return None


def main():
    """메인 함수"""
    # 환경 설정
    setup_environment()

    # 1. State 정의
    GraphState = define_state()

    # 2. 노드 정의
    nodes = define_nodes(GraphState)

    # 3. 기본 RAG 그래프 생성
    basic_app = create_basic_rag_graph(GraphState, nodes)

    # 4. SQL RAG 그래프 생성
    sql_app = create_sql_rag_graph(GraphState, nodes)

    # 5. 그래프 시각화
    visualize_graphs(basic_app, sql_app)

    # 상세 시각화
    visualize_graph_detailed(basic_app, "기본 RAG 그래프")
    visualize_graph_detailed(sql_app, "SQL RAG 그래프")

    # 그래프 비교 시각화
    graphs_dict = {"기본 RAG 그래프": basic_app, "SQL RAG 그래프": sql_app}
    visualize_graph_comparison(graphs_dict)

    # 그래프 요약 정보
    create_graph_summary(basic_app, "기본 RAG 그래프")
    create_graph_summary(sql_app, "SQL RAG 그래프")

    # 실행 흐름 시각화
    visualize_graph_execution_flow(basic_app, "기본 RAG 그래프")
    visualize_graph_execution_flow(sql_app, "SQL RAG 그래프")

    # DOT 형식으로 내보내기
    export_graph_to_dot(basic_app, "기본 RAG 그래프")
    export_graph_to_dot(sql_app, "SQL RAG 그래프")

    # PNG 이미지 생성
    create_graph_png(basic_app, "기본 RAG 그래프")
    create_graph_png(sql_app, "SQL RAG 그래프")

    # 6. 그래프 실행 예제
    initial_state = {
        "context": [],
        "answer": [],
        "question": "테스트 질문",
        "sql_query": "",
        "binary_score": "",
    }

    print("\n" + "=" * 50)
    print("기본 RAG 그래프 실행:")
    run_graph_example(basic_app, initial_state)

    print("\n" + "=" * 50)
    print("SQL RAG 그래프 실행:")
    run_graph_example(sql_app, initial_state)

    print("\n" + "=" * 50)
    print("LangGraph 기본 그래프 생성 예제가 완료되었습니다!")
    print("주석 처리된 부분을 해제하여 다양한 기능을 테스트해보세요.")


if __name__ == "__main__":
    main()
