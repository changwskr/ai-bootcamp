#!/usr/bin/env python3
"""
RAG 기본 구조 이해하기 - 텍스트 문서 기반 RAG 시스템

이 스크립트는 RAG(Retrieval-Augmented Generation)의 기본 구조를 구현합니다.
8단계로 구성된 RAG 파이프라인을 통해 텍스트 문서를 로드하고 질의응답을 수행합니다.

단계:
1. 문서 로드 (Document Load)
2. 문서 분할 (Text Split)
3. 임베딩 생성 (Embedding)
4. 벡터DB 저장 (Vector DB Storage)
5. 검색기 생성 (Retriever)
6. 프롬프트 생성 (Prompt)
7. 언어모델 생성 (LLM)
8. 체인 생성 (Chain)
"""

import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# LangSmith 추적 설정 (선택사항)
try:
    from langchain_teddynote import logging

    logging.langsmith("CH12-RAG")
except ImportError:
    print("LangSmith 추적을 사용하려면 'pip install langchain-teddynote'를 실행하세요.")


def setup_environment():
    """환경 설정 및 API 키 로드"""
    print("=== 환경 설정 ===")
    load_dotenv()
    print("환경변수 로드 완료")


def load_documents(text_path):
    """단계 1: 문서 로드"""
    print("\n=== 단계 1: 문서 로드 ===")
    print(f"텍스트 파일 경로: {text_path}")

    loader = TextLoader(text_path, encoding="utf-8")
    docs = loader.load()
    print(f"문서의 청크 수: {len(docs)}")

    # 첫 번째 청크 내용 미리보기
    if docs:
        print("첫 번째 청크 내용 미리보기:")
        print(docs[0].page_content[:200] + "...")

    return docs


def split_documents(docs, chunk_size=1000, chunk_overlap=50):
    """단계 2: 문서 분할"""
    print("\n=== 단계 2: 문서 분할 ===")
    print(f"청크 크기: {chunk_size}, 오버랩: {chunk_overlap}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    split_documents = text_splitter.split_documents(docs)
    print(f"분할된 청크의 수: {len(split_documents)}")

    # 첫 번째 청크 내용 미리보기
    if split_documents:
        print("첫 번째 청크 내용 미리보기:")
        print(split_documents[0].page_content[:200] + "...")

    return split_documents


def create_embeddings():
    """단계 3: 임베딩 생성"""
    print("\n=== 단계 3: 임베딩 생성 ===")
    embeddings = OpenAIEmbeddings()
    print("OpenAI 임베딩 모델 초기화 완료")
    return embeddings


def create_vectorstore(split_documents, embeddings):
    """단계 4: 벡터DB 생성 및 저장"""
    print("\n=== 단계 4: 벡터DB 생성 및 저장 ===")

    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    print("FAISS 벡터스토어 생성 완료")

    # 테스트 검색
    print("테스트 검색 수행 중...")
    test_results = vectorstore.similarity_search("구글", k=1)
    if test_results:
        print("테스트 검색 결과 미리보기:")
        print(test_results[0].page_content[:200] + "...")

    return vectorstore


def create_retriever(vectorstore):
    """단계 5: 검색기 생성"""
    print("\n=== 단계 5: 검색기 생성 ===")
    retriever = vectorstore.as_retriever()
    print("검색기 생성 완료")

    # 검색기 테스트
    print("검색기 테스트 수행 중...")
    test_query = "삼성전자가 자체 개발한 AI의 이름은?"
    test_results = retriever.invoke(test_query)
    print(f"테스트 쿼리: '{test_query}'")
    print(f"검색된 문서 수: {len(test_results)}")

    return retriever


def create_prompt():
    """단계 6: 프롬프트 생성"""
    print("\n=== 단계 6: 프롬프트 생성 ===")

    prompt = PromptTemplate.from_template(
        """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Answer in Korean.

#Context: 
{context}

#Question:
{question}

#Answer:"""
    )
    print("프롬프트 템플릿 생성 완료")
    return prompt


def create_llm(model_name="gpt-4o-mini", temperature=0):
    """단계 7: 언어모델 생성"""
    print("\n=== 단계 7: 언어모델 생성 ===")
    print(f"모델: {model_name}, Temperature: {temperature}")

    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    print("언어모델 초기화 완료")
    return llm


def create_chain(retriever, prompt, llm):
    """단계 8: 체인 생성"""
    print("\n=== 단계 8: 체인 생성 ===")

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG 체인 생성 완료")
    return chain


def run_rag_chain(chain, question):
    """체인 실행 및 질의응답"""
    print("\n=== RAG 체인 실행 ===")
    print(f"질문: {question}")
    print("-" * 50)

    try:
        response = chain.invoke(question)
        print(f"답변: {response}")
        return response
    except Exception as e:
        print(f"오류 발생: {e}")
        return None


def main():
    """메인 함수 - 전체 RAG 파이프라인 실행"""
    print("RAG 기본 구조 이해하기 - 텍스트 문서 기반 RAG 시스템")
    print("=" * 60)

    # 환경 설정
    setup_environment()

    # 텍스트 파일 경로 (스크립트 위치 기준 상대 경로)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    text_path = os.path.join(script_dir, "data", "SPRI_AI_Brief_2023년12월호_F.txt")

    # 파일 존재 확인
    if not os.path.exists(text_path):
        print(f"오류: 텍스트 파일을 찾을 수 없습니다: {text_path}")
        print("data 폴더에 'SPRI_AI_Brief_2023년12월호_F.txt' 파일을 넣어주세요.")
        return

    try:
        # RAG 파이프라인 실행
        docs = load_documents(text_path)
        split_docs = split_documents(docs)
        embeddings = create_embeddings()
        vectorstore = create_vectorstore(split_docs, embeddings)
        retriever = create_retriever(vectorstore)
        prompt = create_prompt()
        llm = create_llm()
        chain = create_chain(retriever, prompt, llm)

        print("\n" + "=" * 60)
        print("RAG 시스템 구축 완료! 이제 질문을 할 수 있습니다.")
        print("=" * 60)

        # 예시 질문들
        example_questions = [
            "삼성전자가 자체 개발한 AI의 이름은?",
            "구글의 AI 모델은 무엇인가요?",
            "AI 정책과 관련된 주요 내용은 무엇인가요?",
        ]

        for i, question in enumerate(example_questions, 1):
            print(f"\n--- 예시 질문 {i} ---")
            run_rag_chain(chain, question)

        # 사용자 입력 받기
        print("\n" + "=" * 60)
        print("직접 질문을 입력하세요 (종료하려면 'quit' 입력):")
        print("=" * 60)

        while True:
            user_question = input("\n질문을 입력하세요: ").strip()
            if user_question.lower() in ["quit", "exit", "종료"]:
                print("RAG 시스템을 종료합니다.")
                break
            elif user_question:
                run_rag_chain(chain, user_question)
            else:
                print("질문을 입력해주세요.")

    except Exception as e:
        print(f"오류 발생: {e}")
        print("API 키가 올바르게 설정되었는지 확인해주세요.")


if __name__ == "__main__":
    main()
