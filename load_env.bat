@echo off
REM .env 파일에서 환경변수 로드하는 배치 스크립트

if exist src\ai_bootcamp\.env (
    echo Loading environment variables from src\ai_bootcamp\.env file...
    for /f "usebackq tokens=1,* delims==" %%a in ("src\ai_bootcamp\.env") do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
                echo Set: %%a=%%b
            )
        )
    )
    echo Environment variables loaded successfully.
    echo Testing if OPENAI_API_KEY is set...
    echo OPENAI_API_KEY=%OPENAI_API_KEY%
) else if exist .env (
    echo Loading environment variables from .env file...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
                echo Set: %%a=%%b
            )
        )
    )
    echo Environment variables loaded successfully.
    echo Testing if OPENAI_API_KEY is set...
    echo OPENAI_API_KEY=%OPENAI_API_KEY%
) else (
    echo Warning: .env file not found in src\ai_bootcamp\ or root directory. Using system environment variables.
) 