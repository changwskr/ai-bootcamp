import os
import logging
import requests
from dotenv import load_dotenv
from openai import OpenAI
import base64
from PIL import Image
import io

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenAI 환경 변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_DALLE = os.getenv("OPENAI_MODEL_DALLE", "dall-e-3")
OPENAI_MODEL_GPT4V = os.getenv("OPENAI_MODEL_GPT4V", "gpt-4o")

# 기본 이미지 URL
DEFAULT_IMAGE_URL = "https://img.animalplanet.co.kr/news/2019/11/28/700/f9in35p5660ce423x290.jpg"

class ChatImage:
    """OpenAI 이미지 생성 및 분석 클래스"""
    
    def __init__(self):
        """초기화"""
        logger.info("IN: ChatImage.__init__() - ChatImage 초기화")
        
        if not OPENAI_API_KEY:
            logger.error("OUT: ChatImage.__init__() - OPENAI_API_KEY가 설정되지 않음")
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OUT: ChatImage.__init__() - OpenAI 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"OUT: ChatImage.__init__() - OpenAI 클라이언트 초기화 실패: {e}")
            raise
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> str:
        """이미지 생성"""
        logger.info(f"IN: ChatImage.generate_image() - 이미지 생성: prompt={prompt[:50]}...")
        
        try:
            response = self.client.images.generate(
                model=OPENAI_MODEL_DALLE,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"OUT: ChatImage.generate_image() - 이미지 생성 완료: url={image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.generate_image() - 이미지 생성 오류: {e}")
            raise
    
    def analyze_image(self, image_path: str, prompt: str = "이 이미지를 분석해주세요.") -> str:
        """이미지 분석 (로컬 파일)"""
        logger.info(f"IN: ChatImage.analyze_image() - 이미지 분석: image_path={image_path}")
        
        try:
            # 이미지 파일 읽기
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # 이미지 분석 요청
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL_GPT4V,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"OUT: ChatImage.analyze_image() - 이미지 분석 완료")
            return analysis
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.analyze_image() - 이미지 분석 오류: {e}")
            raise
    
    def analyze_image_url(self, image_url: str, prompt: str = "이 이미지를 분석해주세요.") -> str:
        """이미지 분석 (URL)"""
        logger.info(f"IN: ChatImage.analyze_image_url() - 이미지 분석: image_url={image_url}")
        
        try:
            # 이미지 분석 요청 (URL 직접 사용)
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL_GPT4V,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"OUT: ChatImage.analyze_image_url() - 이미지 분석 완료")
            return analysis
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.analyze_image_url() - 이미지 분석 오류: {e}")
            raise
    
    def download_image(self, image_url: str, save_path: str = "downloaded_image.jpg", verify_ssl: bool = False) -> str:
        """이미지 다운로드"""
        logger.info(f"IN: ChatImage.download_image() - 이미지 다운로드: image_url={image_url}, verify_ssl={verify_ssl}")
        
        try:
            # 이미지 다운로드 (SSL 검증 옵션 포함)
            response = requests.get(image_url, stream=True, verify=verify_ssl)
            response.raise_for_status()
            
            # 이미지 저장
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"OUT: ChatImage.download_image() - 이미지 다운로드 완료: save_path={save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.download_image() - 이미지 다운로드 오류: {e}")
            raise
    
    def test_image_generation(self, prompt: str = "A cute cat sitting on a laptop") -> None:
        """이미지 생성 테스트"""
        logger.info(f"IN: ChatImage.test_image_generation() - 이미지 생성 테스트: prompt={prompt}")
        
        try:
            print("🎨 OpenAI 이미지 생성 테스트")
            print("=" * 50)
            
            # 이미지 생성
            image_url = self.generate_image(prompt)
            
            print(f"📝 프롬프트: {prompt}")
            print(f"🖼️ 생성된 이미지 URL: {image_url}")
            print(f"✅ 이미지 생성 완료!")
            
            logger.info("OUT: ChatImage.test_image_generation() - 이미지 생성 테스트 완료")
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.test_image_generation() - 이미지 생성 테스트 오류: {e}")
            print(f"❌ 오류 발생: {e}")
    
    def test_image_analysis(self, image_path: str = "test_image.jpg") -> None:
        """이미지 분석 테스트 (로컬 파일)"""
        logger.info(f"IN: ChatImage.test_image_analysis() - 이미지 분석 테스트: image_path={image_path}")
        
        try:
            print("🔍 OpenAI 이미지 분석 테스트 (로컬 파일)")
            print("=" * 50)
            
            # 이미지 분석
            analysis = self.analyze_image(image_path)
            
            print(f"📁 이미지 파일: {image_path}")
            print(f"🔍 분석 결과: {analysis}")
            print(f"✅ 이미지 분석 완료!")
            
            logger.info("OUT: ChatImage.test_image_analysis() - 이미지 분석 테스트 완료")
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.test_image_analysis() - 이미지 분석 테스트 오류: {e}")
            print(f"❌ 오류 발생: {e}")
    
    def test_image_analysis_url(self, image_url: str = DEFAULT_IMAGE_URL) -> None:
        """이미지 분석 테스트 (URL)"""
        logger.info(f"IN: ChatImage.test_image_analysis_url() - 이미지 분석 테스트: image_url={image_url}")
        
        try:
            print("🔍 OpenAI 이미지 분석 테스트 (URL)")
            print("=" * 50)
            
            # 이미지 분석
            analysis = self.analyze_image_url(image_url)
            
            print(f"🌐 이미지 URL: {image_url}")
            print(f"🔍 분석 결과: {analysis}")
            print(f"✅ 이미지 분석 완료!")
            
            logger.info("OUT: ChatImage.test_image_analysis_url() - 이미지 분석 테스트 완료")
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.test_image_analysis_url() - 이미지 분석 테스트 오류: {e}")
            print(f"❌ 오류 발생: {e}")
    
    def test_image_download_and_analysis(self, image_url: str = DEFAULT_IMAGE_URL) -> None:
        """이미지 다운로드 및 분석 테스트"""
        logger.info(f"IN: ChatImage.test_image_download_and_analysis() - 이미지 다운로드 및 분석 테스트: image_url={image_url}")
        
        try:
            print("📥 이미지 다운로드 및 분석 테스트")
            print("=" * 50)
            
            # 이미지 다운로드 (SSL 검증 비활성화)
            save_path = self.download_image(image_url, "animal_planet_image.jpg", verify_ssl=False)
            print(f"📥 이미지 다운로드 완료: {save_path}")
            
            # 다운로드한 이미지 분석
            analysis = self.analyze_image(save_path, "이 이미지에 어떤 동물이 있나요? 자세히 설명해주세요.")
            
            print(f"🔍 분석 결과: {analysis}")
            print(f"✅ 이미지 다운로드 및 분석 완료!")
            
            logger.info("OUT: ChatImage.test_image_download_and_analysis() - 이미지 다운로드 및 분석 테스트 완료")
            
        except Exception as e:
            logger.error(f"OUT: ChatImage.test_image_download_and_analysis() - 이미지 다운로드 및 분석 테스트 오류: {e}")
            print(f"❌ 오류 발생: {e}")

def main():
    """메인 함수"""
    logger.info("IN: main() - 프로그램 시작")
    
    try:
        # ChatImage 인스턴스 생성
        chat_image = ChatImage()
        
        print("🎨 OpenAI 이미지 처리 데모")
        print("=" * 60)
        
        # 1. 이미지 생성 테스트
        print("\n1️⃣ 이미지 생성 테스트")
        chat_image.test_image_generation("A beautiful sunset over mountains")
        
        # 2. URL 이미지 분석 테스트
        print("\n2️⃣ URL 이미지 분석 테스트")
        chat_image.test_image_analysis_url()
        
        # 3. 이미지 다운로드 및 분석 테스트
        print("\n3️⃣ 이미지 다운로드 및 분석 테스트")
        try:
            chat_image.test_image_download_and_analysis()
        except Exception as e:
            print(f"⚠️ 다운로드 실패, URL 직접 분석으로 대체: {e}")
            print("🔄 URL 직접 분석으로 진행...")
            chat_image.test_image_analysis_url()
        
        # 4. 로컬 파일 이미지 분석 테스트 (파일이 있는 경우)
        # print("\n4️⃣ 로컬 파일 이미지 분석 테스트")
        # chat_image.test_image_analysis("animal_planet_image.jpg")
        
        logger.info("OUT: main() - 프로그램 완료")
        
    except Exception as e:
        logger.error(f"OUT: main() - 프로그램 오류: {e}")
        print(f"❌ 프로그램 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()