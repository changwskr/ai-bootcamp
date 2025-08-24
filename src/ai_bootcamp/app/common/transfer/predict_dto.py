from pydantic import BaseModel


class PredictRequestDto(BaseModel):
    """예측 요청 DTO"""

    text: str


class PredictResponseDto(BaseModel):
    """예측 응답 DTO"""

    label: str
    score: float
