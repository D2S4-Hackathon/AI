import openai
from typing import Optional
from config.naver_stt_settings import settings, logger
from models.stt_models import SummaryResponse

class OpenAIService:
    """OpenAI API를 활용한 텍스트 요약 서비스"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        try:
            # 단순한 방식으로 API 키 설정
            openai.api_key = settings.OPENAI_API_KEY
            
            self.model = settings.OPENAI_MODEL
            self.max_summary_length = settings.MAX_SUMMARY_LENGTH
            self.min_text_length = settings.MIN_TEXT_LENGTH_FOR_SUMMARY
            
            logger.info(f"OpenAI 서비스가 성공적으로 초기화되었습니다. (모델: {self.model})")
            
        except Exception as e:
            logger.error(f"OpenAI 서비스 초기화 실패: {str(e)}")
            raise ValueError(f"OpenAI 서비스 초기화 실패: {str(e)}")
    
    def summarize_text(self, text: str, language: str = "ko") -> SummaryResponse:
        """
        텍스트를 요약합니다.
        
        Args:
            text (str): 요약할 텍스트
            language (str): 요약 언어 ('ko', 'en', 'ja', 'zh')
        
        Returns:
            SummaryResponse: 요약 결과
        """
        try:
            # 언어별 프롬프트 설정
            prompts = {
                "ko": """당신은 뉴스 분석 AI입니다. 입력된 텍스트를 분석하여 다음과 같이 응답해주세요:

**케이스 1: 검색 결과 페이지인 경우**
- 텍스트에 "검색결과", "관련도순", "최신순" 등이 포함되어 있으면
- "[주제] 관련 뉴스를 검색하면 다음과 같은 헤드라인들을 볼 수 있습니다:"로 시작
- 발견된 뉴스 헤드라인들을 "첫째, [제목] - [한 줄 요약]" "둘째, [제목] - [한 줄 요약]" 형식으로 순서대로 나열
- "더 자세한 정보가 필요한 뉴스가 있다면 해당 뉴스 내용을 알려주세요."로 마무리

**케이스 2: 구체적인 뉴스 기사인 경우**
- 특정 언론사 기사 내용이 포함되어 있으면
- 기사의 핵심 내용을 3-4문장으로 간결하게 요약
- 5W1H (누가, 언제, 어디서, 무엇을, 왜, 어떻게)를 중심으로 정리
- 중요한 키워드와 수치는 정확히 포함

현재 입력된 텍스트를 분석하여 적절한 형식으로 응답해주세요."""
            }
            
            system_prompt = prompts.get(language, prompts["ko"])
            
            # OpenAI API 호출 (구버전 방식)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                top_p=0.9
            )
            
            summary = response.choices[0].message.content.strip()
            
            # 결과 계산
            original_length = len(text)
            summary_length = len(summary)
            compression_ratio = round((1 - summary_length / original_length) * 100, 2)
            
            logger.info(f"텍스트 요약 완료: {original_length}자 → {summary_length}자 (압축률: {compression_ratio}%)")
            
            return SummaryResponse(
                success=True,
                original_text=text,
                summary=summary,
                original_length=original_length,
                summary_length=summary_length,
                compression_ratio=compression_ratio
            )
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"요약 처리 중 오류: {error_message}")
            
            # 오류 타입별 처리
            if "rate_limit_exceeded" in error_message or "rate limit" in error_message.lower():
                return SummaryResponse(
                    success=False,
                    error="API 사용량 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
                )
            elif "invalid_api_key" in error_message or "authentication" in error_message.lower():
                return SummaryResponse(
                    success=False,
                    error="API 키 인증에 실패했습니다."
                )
            elif "model_not_found" in error_message or "model" in error_message.lower():
                return SummaryResponse(
                    success=False,
                    error=f"지원하지 않는 모델입니다: {self.model}"
                )
            else:
                return SummaryResponse(
                    success=False,
                    error=f"요약 처리 중 오류가 발생했습니다: {error_message}"
                )
    
    def get_service_status(self) -> bool:
        """OpenAI 서비스 상태를 확인합니다."""
        try:
            # 간단한 테스트 요청으로 서비스 상태 확인
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.warning(f"OpenAI 서비스 상태 확인 실패: {str(e)}")
            return False
