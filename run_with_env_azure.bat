@echo off
REM .env 파일을 로드하고 Azure OpenAI Python 스크립트를 실행하는 배치 스크립트

echo Loading environment variables and running Azure OpenAI Python script...

REM .env 파일에서 환경변수 로드
if exist src\ai_bootcamp\.env (
    echo Loading from src\ai_bootcamp\.env...
    for /f "usebackq tokens=1,* delims==" %%a in ("src\ai_bootcamp\.env") do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
                echo Set: %%a=%%b
            )
        )
    )
) else if exist .env (
    echo Loading from .env...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
                echo Set: %%a=%%b
            )
        )
    )
) else (
    echo Warning: .env file not found.
)

echo Environment variables loaded.
echo Testing AZURE_OPENAI_API_KEY: %AZURE_OPENAI_API_KEY%

REM Python 스크립트 실행 (같은 프로세스에서)
set PYTHONPATH=src
.venv\Scripts\python.exe src\ai_bootcamp\app\demo\multiagent\trymultiagentchat.py 