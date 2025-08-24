import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo/prac01", tags=["데모 - 실습01"])


class DemoController:
    """데모 실습01 컨트롤러"""

    def __init__(self):
        self.templates_path = (
            Path(__file__).parent.parent.parent.parent / "resources" / "templates"
        )

    async def demo_page(self):
        """데모 페이지"""
        logger.info("IN: DemoController.demo_page() - 데모 페이지 요청")
        try:
            response = FileResponse(
                str(self.templates_path / "demo" / "prac01" / "index.html")
            )
            logger.info("OUT: DemoController.demo_page() - 데모 페이지 반환 성공")
            return response
        except Exception as e:
            logger.error(f"OUT: DemoController.demo_page() - 오류 발생: {e}")
            raise

    async def hello(self):
        """Hello API"""
        logger.info("IN: DemoController.hello() - Hello API 요청")
        try:
            response = {"message": "Hello from Prac01 Demo!", "status": "success"}
            logger.info("OUT: DemoController.hello() - Hello API 응답 완료")
            return response
        except Exception as e:
            logger.error(f"OUT: DemoController.hello() - 오류 발생: {e}")
            raise


# 컨트롤러 인스턴스 생성
demo_controller = DemoController()

# 라우터에 컨트롤러 메서드 등록
router.add_api_route("/", demo_controller.demo_page, methods=["GET"], response_class=HTMLResponse)
router.add_api_route("/hello", demo_controller.hello, methods=["GET"])
 