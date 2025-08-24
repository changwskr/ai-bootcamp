from fastapi import HTTPException

from ...transfer.predict_dto import PredictRequestDto, PredictResponseDto
from ..dc.predict_dc import PredictDC
from ..dc.repository.predict_dao import PredictDAO


class PredictService:
    """예측 관련 비즈니스 로직"""

    def __init__(self):
        self.predict_dc = PredictDC()
        self.predict_dao = PredictDAO()

    def predict_text(self, request: PredictRequestDto) -> PredictResponseDto:
        """텍스트 예측 처리"""
        # API 키 검증
        if not self.predict_dc.validate_api_key():
            raise HTTPException(status_code=500, detail="API key not configured")

        # 예측 수행
        result = self.predict_dc.process_prediction(request.text)

        # 예측 결과 DB 저장
        self.predict_dao.save_prediction(request.text, result["label"], result["score"])

        return PredictResponseDto(label=result["label"], score=result["score"])

    def get_model_info(self) -> dict:
        """모델 정보 조회"""
        dc_info = self.predict_dc.get_model_info()
        dao_info = self.predict_dao.get_model_info()

        return {**dc_info, "db_info": dao_info}

    def get_system_config(self) -> dict:
        """시스템 설정 정보 조회"""
        model_info = self.predict_dc.get_model_info()

        return {
            "mlflow_tracking_uri": model_info["mlflow_tracking_uri"],
            "api_key_configured": model_info["api_key_configured"],
            "model_name": model_info["model_name"],
            "model_type": model_info["model_type"],
        }

    def get_prediction_stats(self) -> dict:
        """예측 통계 조회"""
        return self.predict_dao.get_prediction_stats()
