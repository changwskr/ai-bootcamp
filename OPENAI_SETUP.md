# OpenAI 설정 가이드

## 🔑 환경 변수 설정

### 1. OpenAI API 키 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI 모델 설정 (선택사항 - 기본값 사용)
OPENAI_MODEL_GPT4=gpt-4
OPENAI_MODEL_GPT35=gpt-3.5-turbo
OPENAI_MODEL_GPT4O=gpt-4o
OPENAI_MODEL_GPT4O_MINI=gpt-4o-mini
```

### 2. OpenAI API 키 발급

1. [OpenAI 웹사이트](https://platform.openai.com/)에 접속
2. 계정 생성 또는 로그인
3. API Keys 메뉴에서 새 API 키 생성
4. 생성된 키를 `OPENAI_API_KEY`에 설정

## 🚀 사용 방법

### 1. 직접 실행

```bash
# 환경 변수 설정
set OPENAI_API_KEY=your_api_key_here

# 프로그램 실행
python src/ai_bootcamp/app/demo/prac01/chatdemo.py
```

### 2. Makefile 사용

```bash
# Makefile에 다음 타겟 추가 후 사용
make chat-demo
```

## 📝 주요 기능

### ChatDemo 클래스

- `chat_completion()`: 채팅 완성 API 호출
- `get_available_models()`: 사용 가능한 모델 목록 조회
- `test_chat()`: 채팅 테스트 실행

### 지원 모델

- `gpt-4`: GPT-4 모델
- `gpt-3.5-turbo`: GPT-3.5 Turbo 모델
- `gpt-4o`: GPT-4o 모델
- `gpt-4o-mini`: GPT-4o Mini 모델 (기본값)

## 🔧 로깅

모든 API 호출에 대해 상세한 로그가 출력됩니다:

```
2024-01-XX XX:XX:XX,XXX - ChatDemo - INFO - IN: ChatDemo.chat_completion() - 채팅 요청
2024-01-XX XX:XX:XX,XXX - ChatDemo - INFO - OUT: ChatDemo.chat_completion() - 채팅 완료
```

## ⚠️ 주의사항

1. API 키는 절대 공개하지 마세요
2. `.env` 파일을 `.gitignore`에 추가하세요
3. API 사용량에 따른 비용이 발생할 수 있습니다 