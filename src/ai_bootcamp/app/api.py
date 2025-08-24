import os
import logging
from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI

# .env 파일 로드
load_dotenv()
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .common.transfer.auth_dto import LoginRequestDto
from .common.web.account_controller import router as account_router
from .common.web.auth_controller import auth_controller
from .common.web.auth_controller import router as auth_router
from .common.web.predict_controller import predict_controller
from .common.web.predict_controller import router as predict_router
from .common.web.account_controller import account_controller
from .common.web.account_controller import router as account_router
from .demo.prac01.demo_controller import router as demo_router
from .demo.prac02.demo_controller import router as demo_prac02_router
from .demo.prac02.langchain_controller import router as langchain_router
from .demo.prac02.langchain_api_controller import router as langchain_api_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="AI Bootcamp API")

# 정적 파일 서빙 설정
static_path = Path(__file__).parent.parent / "resources" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 이미지 파일을 static 디렉토리 내부에 저장하도록 설정
images_path = static_path / "images"
if not images_path.exists():
    images_path.mkdir(parents=True, exist_ok=True)

# 라우터 등록
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(account_router)
app.include_router(demo_router)
app.include_router(demo_prac02_router)
app.include_router(langchain_router)
app.include_router(langchain_api_router)


# 루트 페이지 - 로그인 페이지로 리다이렉트
@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 페이지 - 로그인 페이지로 리다이렉트"""
    logger.info("IN: root() - 루트 페이지 요청")
    try:
        response = FileResponse(
            str(
                Path(__file__).parent.parent
                / "resources"
                / "templates"
                / "login"
                / "index.html"
            )
        )
        logger.info("OUT: root() - 로그인 페이지 반환 성공")
        return response
    except Exception as e:
        logger.error(f"OUT: root() - 오류 발생: {e}")
        raise


# 기존 엔드포인트들 (하위 호환성을 위해 유지)
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """로그인 페이지"""
    logger.info("IN: login_page() - 로그인 페이지 요청")
    try:
        response = await auth_controller.login_page()
        logger.info("OUT: login_page() - 로그인 페이지 반환 성공")
        return response
    except Exception as e:
        logger.error(f"OUT: login_page() - 오류 발생: {e}")
        raise


@app.post("/login")
async def login(request: LoginRequestDto):
    """로그인 처리"""
    logger.info(f"IN: login() - 로그인 요청: username={request.username}")
    try:
        response = await auth_controller.login(request)
        logger.info(f"OUT: login() - 로그인 처리 완료: username={request.username}")
        return response
    except Exception as e:
        logger.error(
            f"OUT: login() - 로그인 오류 발생: username={request.username}, error={e}"
        )
        raise


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """대시보드 페이지"""
    logger.info("IN: dashboard() - 대시보드 페이지 요청")
    try:
        response = await auth_controller.dashboard()
        logger.info("OUT: dashboard() - 대시보드 페이지 반환 성공")
        return response
    except Exception as e:
        logger.error(f"OUT: dashboard() - 오류 발생: {e}")
        raise


@app.get("/accounts", response_class=HTMLResponse)
async def accounts_page():
    """계정 관리 페이지"""
    logger.info("IN: accounts_page() - 계정 관리 페이지 요청")
    try:
        response = await account_controller.accounts_page()
        logger.info("OUT: accounts_page() - 계정 관리 페이지 반환 성공")
        return response
    except Exception as e:
        logger.error(f"OUT: accounts_page() - 오류 발생: {e}")
        raise


@app.post("/logout")
async def logout():
    """로그아웃 처리"""
    logger.info("IN: logout() - 로그아웃 요청")
    try:
        response = await auth_controller.logout()
        logger.info("OUT: logout() - 로그아웃 처리 완료")
        return response
    except Exception as e:
        logger.error(f"OUT: logout() - 로그아웃 오류 발생: {e}")
        raise


@app.get("/health")
def health():
    """헬스 체크"""
    logger.info("IN: health() - 헬스 체크 요청")
    try:
        config = predict_controller.predict_service.get_system_config()
        response = {
            "status": "ok",
            "mlflow_tracking_uri": config["mlflow_tracking_uri"],
            "api_key_configured": config["api_key_configured"],
        }
        logger.info("OUT: health() - 헬스 체크 완료")
        return response
    except Exception as e:
        logger.error(f"OUT: health() - 헬스 체크 오류 발생: {e}")
        raise


@app.post("/predict")
def predict(request):
    """예측 처리"""
    logger.info(f"IN: predict() - 예측 요청: {request}")
    try:
        response = predict_controller.predict_service.predict_text(request)
        logger.info("OUT: predict() - 예측 처리 완료")
        return response
    except Exception as e:
        logger.error(f"OUT: predict() - 예측 오류 발생: {e}")
        raise


@app.get("/config")
def get_config():
    """환경 설정 정보를 반환하는 엔드포인트"""
    logger.info("IN: get_config() - 설정 정보 요청")
    try:
        response = predict_controller.predict_service.get_system_config()
        logger.info("OUT: get_config() - 설정 정보 반환 완료")
        return response
    except Exception as e:
        logger.error(f"OUT: get_config() - 설정 정보 오류 발생: {e}")
        raise
