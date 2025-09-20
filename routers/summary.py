from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.openai_service import OpenAIService
from models.stt_models import SummaryResponse
from core.exceptions.stt_exceptions import (
    validate_summary_text, 
    validate_summary_parameters
)
from config.naver_stt_settings import logger
from utils.redis_utils import r   # Redis 클라이언트 가져오기
import json

router = APIRouter(prefix="/summary", tags=["Summary"])

# 서비스 인스턴스 생성
try:
    openai_service = OpenAIService()
    logger.info("요약 서비스가 성공적으로 초기화되었습니다.")
except Exception as e:
    logger.warning(f"요약 서비스 초기화 실패: {e}")
    openai_service = None


@router.post("/text", response_model=SummaryResponse)
async def summarize_text(context_session_id: str, language: str = "ko"):
    """텍스트만 요약합니다."""
    if not openai_service:
        raise HTTPException(status_code=503, detail="요약 서비스를 사용할 수 없습니다.")

    raw_context = r.get(f"context:{context_session_id}")
    if not raw_context:
        raise HTTPException(status_code=404, detail="해당 세션의 본문을 찾을 수 없습니다.")

    try:
        context_data = json.loads(raw_context)
        text = context_data.get("inner_text", "")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="본문 데이터를 불러오는 중 오류가 발생했습니다.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="본문이 비어 있습니다.")
    # 입력 검증
    # validate_summary_text(request.text)
    # validate_summary_parameters(request.language)
    validate_summary_parameters(language)

    try:
        logger.info(f"텍스트 요약 요청: 길이={len(text)}자, 언어={language}")
        
        result = openai_service.summarize_text(
            text=text,
            language=language
        )
        
        if result.success:
            logger.info("텍스트 요약 성공")
        else:
            logger.error("텍스트 요약 실패")

        # return result

        # 수정 포인트: result 전체가 아니라 SummaryResponse에 맞춰 반환
        return SummaryResponse(
            status="success",
            summary=result.summary if result.success else ""
        )

    except Exception as e:
        logger.error(f"텍스트 요약 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 처리 중 오류: {str(e)}")


@router.get("/status")
async def get_summary_service_status():
    """요약 서비스 상태를 반환합니다."""
    try:
        openai_available = openai_service is not None
        if openai_service:
            openai_available = openai_service.get_service_status()
    except:
        openai_available = False
    
    return JSONResponse(content={
        "status": "ok" if openai_available else "unavailable",
        "openai_service_available": openai_available
    })
