import logging

from fastapi import APIRouter

from ..business.aps.predict_service import PredictService
from ..transfer.predict_dto import PredictRequestDto, PredictResponseDto

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["예측"])


class PredictController:
    """예측 관련 웹 컨트롤러"""

    def __init__(self):
        self.predict_service = PredictService()

    @router.post("/text")
    async def predict_text(self, request: PredictRequestDto) -> PredictResponseDto:
        """텍스트 예측"""
        logger.info(f"IN: PredictController.predict_text() - 예측 요청: {request}")
        try:
            response = self.predict_service.predict_text(request)
            logger.info("OUT: PredictController.predict_text() - 예측 처리 완료")
            return response
        except Exception as e:
            logger.error(f"OUT: PredictController.predict_text() - 예측 오류 발생: {e}")
            raise

    @router.get("/model-info")
    async def get_model_info(self):
        """모델 정보 조회"""
        logger.info("IN: PredictController.get_model_info() - 모델 정보 조회 요청")
        try:
            response = self.predict_service.get_model_info()
            logger.info("OUT: PredictController.get_model_info() - 모델 정보 조회 완료")
            return response
        except Exception as e:
            logger.error(
                f"OUT: PredictController.get_model_info() - 모델 정보 조회 오류: {e}"
            )
            raise

    @router.get("/config")
    async def get_system_config(self):
        """시스템 설정 정보 조회"""
        logger.info("IN: PredictController.get_system_config() - 시스템 설정 조회 요청")
        try:
            response = self.predict_service.get_system_config()
            logger.info(
                "OUT: PredictController.get_system_config() - 시스템 설정 조회 완료"
            )
            return response
        except Exception as e:
            logger.error(
                f"OUT: PredictController.get_system_config() - 시스템 설정 조회 오류: {e}"
            )
            raise


# 컨트롤러 인스턴스 생성
predict_controller = PredictController()
