#!/usr/bin/env python3
"""
Demo Controller for Prac02 (Image Demo)
Prac02 이미지 데모를 위한 웹 컨트롤러
"""

import logging
import os
import requests
import uuid
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import io

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo/prac02", tags=["demo"])


class ImageGenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"


class ImageAnalysisRequest(BaseModel):
    prompt: str


class DemoController:
    """Prac02 데모 컨트롤러"""

    def __init__(self):
        self.templates_path = (
            Path(__file__).parent.parent.parent.parent / "resources" / "templates"
        )
        self.images_path = (
            Path(__file__).parent.parent.parent.parent / "resources" / "static" / "images"
        )
        # 이미지 저장 디렉토리 생성
        self.images_path.mkdir(parents=True, exist_ok=True)

    async def demo_page(self):
        """이미지 데모 페이지"""
        logger.info("IN: DemoController.demo_page() - 이미지 데모 페이지 요청")
        try:
            response = FileResponse(
                str(self.templates_path / "demo" / "prac02" / "index.html")
            )
            logger.info("OUT: DemoController.demo_page() - 이미지 데모 페이지 반환 성공")
            return response
        except Exception as e:
            logger.error(f"OUT: DemoController.demo_page() - 오류 발생: {e}")
            raise

    async def hello(self):
        """Hello API"""
        logger.info("IN: DemoController.hello() - Hello API 요청")
        try:
            response = {"message": "Hello from Prac02 Image Demo!", "status": "success"}
            logger.info("OUT: DemoController.hello() - Hello API 응답 완료")
            return response
        except Exception as e:
            logger.error(f"OUT: DemoController.hello() - 오류 발생: {e}")
            raise

    async def generate_image(self, request: ImageGenerationRequest):
        """이미지 생성 API"""
        logger.info(f"IN: DemoController.generate_image() - 이미지 생성 요청: prompt={request.prompt}")
        try:
            use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
            
            if use_mock:
                # Mock 모드: 로컬에서 이미지 생성
                logger.info("generate_image() - Mock 모드로 이미지 생성")
                
                # 고유한 파일명 생성
                image_filename = f"generated_mock_{uuid.uuid4().hex[:8]}.png"
                image_path = self.images_path / image_filename
                
                # Mock 이미지 생성 (PIL 사용)
                width, height = map(int, request.size.split('x'))
                img = Image.new('RGB', (width, height), color='#007bff')
                draw = ImageDraw.Draw(img)
                
                # 텍스트 추가
                try:
                    # 기본 폰트 사용 (폰트가 없을 경우를 대비)
                    font_size = min(width, height) // 20
                    font = ImageFont.load_default()
                except:
                    font = None
                
                text = f"Mock Image\nPrompt: {request.prompt[:50]}..."
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                
                draw.text((x, y), text, fill='white', font=font)
                
                # 이미지 저장
                img.save(image_path, 'PNG')
                
                local_image_url = f"/static/images/{image_filename}"
                logger.info(f"generate_image() - Mock 이미지 생성 완료: {image_path}")
                
            else:
                # 실제 OpenAI API 호출
                logger.info("generate_image() - OpenAI API 호출 시작")
                openai_api_key = os.getenv("OPENAI_API_KEY")
                
                if not openai_api_key:
                    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
                
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                
                # 이미지 생성 요청
                dalle_response = client.images.generate(
                    model="dall-e-3",
                    prompt=request.prompt,
                    size=request.size,
                    quality=request.quality,
                    n=1
                )
                
                generated_image_url = dalle_response.data[0].url
                logger.info(f"generate_image() - OpenAI 이미지 생성 성공: {generated_image_url}")
                
                # 생성된 이미지 다운로드
                image_filename = f"generated_{uuid.uuid4().hex[:8]}.png"
                image_path = self.images_path / image_filename
                
                try:
                    response_img = requests.get(generated_image_url, timeout=30)
                    response_img.raise_for_status()
                    
                    with open(image_path, 'wb') as f:
                        f.write(response_img.content)
                    
                    local_image_url = f"/static/images/{image_filename}"
                    logger.info(f"generate_image() - 이미지 다운로드 완료: {image_path}")
                except Exception as download_error:
                    logger.warning(f"generate_image() - 이미지 다운로드 실패, Mock 이미지로 대체: {download_error}")
                    # 다운로드 실패 시 Mock 이미지 생성
                    width, height = map(int, request.size.split('x'))
                    img = Image.new('RGB', (width, height), color='#28a745')
                    draw = ImageDraw.Draw(img)
                    
                    text = f"OpenAI Generated\nPrompt: {request.prompt[:50]}...\n(Download failed, using mock)"
                    bbox = draw.textbbox((0, 0), text, font=None)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (width - text_width) // 2
                    y = (height - text_height) // 2
                    
                    draw.text((x, y), text, fill='white', font=None)
                    img.save(image_path, 'PNG')
                    
                    local_image_url = f"/static/images/{image_filename}"
            
            response = {
                "image_url": local_image_url,
                "local_path": str(image_path),
                "filename": image_filename,
                "prompt": request.prompt,
                "size": request.size,
                "quality": request.quality,
                "mock_mode": use_mock,
                "status": "success"
            }
            
            logger.info(f"OUT: DemoController.generate_image() - 이미지 생성 및 저장 성공: {local_image_url}")
            return JSONResponse(content=response)
            
        except Exception as e:
            logger.error(f"OUT: DemoController.generate_image() - 오류 발생: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"이미지 생성 중 오류가 발생했습니다: {str(e)}"}
            )

    async def analyze_image(self, image: UploadFile = File(...), prompt: str = Form(...)):
        """이미지 분석 API"""
        logger.info(f"IN: DemoController.analyze_image() - 이미지 분석 요청: filename={image.filename}, prompt={prompt}")
        try:
            # Mock 응답 (실제 OpenAI API 호출 대신)
            mock_analysis = f"이미지 '{image.filename}'에 대한 분석 결과입니다. 요청하신 프롬프트 '{prompt}'에 따라 분석한 결과: 이 이미지는 테스트용 이미지로 보이며, 실제 분석 기능은 Mock 모드에서 제공됩니다."
            
            response = {
                "analysis": mock_analysis,
                "filename": image.filename,
                "prompt": prompt,
                "status": "success"
            }
            
            logger.info(f"OUT: DemoController.analyze_image() - 이미지 분석 성공")
            return JSONResponse(content=response)
        except Exception as e:
            logger.error(f"OUT: DemoController.analyze_image() - 오류 발생: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"이미지 분석 중 오류가 발생했습니다: {str(e)}"}
            )


# 컨트롤러 인스턴스 생성
demo_controller = DemoController()

# 라우터에 컨트롤러 메서드 등록
router.add_api_route("/", demo_controller.demo_page, methods=["GET"], response_class=HTMLResponse)
router.add_api_route("/hello", demo_controller.hello, methods=["GET"])
router.add_api_route("/generate-image", demo_controller.generate_image, methods=["POST"])
router.add_api_route("/analyze-image", demo_controller.analyze_image, methods=["POST"]) 