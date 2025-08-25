#!/bin/bash

# RAG Basic PDF 스크립트 실행을 위한 패키지 설치 스크립트

echo "RAG 스크립트 실행을 위한 패키지 설치를 시작합니다..."

# 기본 환경 설정
pip install python-dotenv>=1.0.0

# LangChain 핵심 패키지들
pip install langchain-core>=0.1.0
pip install langchain-openai>=0.1.0
pip install langchain-text-splitters>=0.1.0
pip install langchain-community>=0.1.0

# 벡터 데이터베이스
pip install faiss-cpu>=1.7.0

# OpenAI API
pip install openai>=1.0.0

# 추가 유틸리티 (선택사항)
pip install numpy>=1.21.0
pip install pandas>=1.3.0

echo "패키지 설치가 완료되었습니다!"
echo "이제 'python rag_basic_pdf.py' 명령어로 스크립트를 실행할 수 있습니다." 