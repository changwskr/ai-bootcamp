#!/bin/bash

# LangGraph 기본 그래프 생성 예제를 위한 패키지 설치 스크립트

echo "LangGraph 예제 실행을 위한 패키지 설치를 시작합니다..."

# 기본 환경 설정
pip install python-dotenv>=1.0.0

# LangChain 핵심 패키지들
pip install langchain-core>=0.1.0
pip install langchain-openai>=0.1.0
pip install langchain-text-splitters>=0.1.0
pip install langchain-community>=0.1.0

# LangGraph 패키지
pip install langgraph>=0.1.0

# 그래프 시각화 (LangSmith 추적용)
pip install langchain-teddynote>=0.1.0

# OpenAI API
pip install openai>=1.0.0

# 추가 유틸리티 (선택사항)
pip install numpy>=1.21.0
pip install pandas>=1.3.0

echo "패키지 설치가 완료되었습니다!"
echo "이제 'python 01-langgraph-building-graph.py' 명령어로 스크립트를 실행할 수 있습니다."
echo "또는 'make langgraph-building-graph' 명령어를 사용하세요." 