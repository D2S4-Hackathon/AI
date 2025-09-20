from fastapi import HTTPException
from fastapi.responses import JSONResponse
from config.naver_stt_settings import logger


class STTException(Exception):

  def __init__(self, message: str, code: str = None):
    self.message = message
    self.code = code
    super().__init__(self.message)


class SummaryException(Exception):
  """요약 관련 예외"""

  def __init__(self, message: str, code: str = None):
    self.message = message
    self.code = code
    super().__init__(self.message)


class VoiceOrderException(Exception):

  def __init__(self, message: str, code: str = None):
    self.message = message
    self.code = code
    super().__init__(self.message)


def handle_stt_errors(result: dict) -> JSONResponse:
  if result["success"]:
    return None

  # 네이버 STT 특정 오류 처리
  details = str(result.get("details", ""))

  if "STT007" in details:
    return JSONResponse(content={
      "success": False,
      "error": "음성이 너무 짧거나 인식할 수 없습니다. 더 길게 말씀해주세요.",
      "code": "AUDIO_TOO_SHORT"
    })
  elif "STT006" in details:
    return JSONResponse(content={
      "success": False,
      "error": "지원하지 않는 오디오 형식입니다.",
      "code": "UNSUPPORTED_FORMAT"
    })

  return JSONResponse(content=result)


def validate_audio_file(audio_data: bytes, filename: str = None) -> None:
  from config.naver_stt_settings import settings

  if len(audio_data) == 0:
    raise HTTPException(status_code=400, detail="비어있는 오디오 파일입니다.")

  if len(audio_data) > settings.MAX_FILE_SIZE:
    raise HTTPException(status_code=400, detail="파일 크기가 너무 큽니다. (최대 50MB)")

  if len(audio_data) < settings.MIN_FILE_SIZE:
    raise HTTPException(
        status_code=400,
        detail="음성이 너무 짧습니다. 최소 1초 이상 녹음해주세요."
    )


def validate_language(lang: str) -> None:
  from config.naver_stt_settings import settings

  if lang not in settings.SUPPORTED_LANGUAGES:
    raise HTTPException(
        status_code=400,
        detail=f"지원되지 않는 언어입니다. 지원 언어: {settings.SUPPORTED_LANGUAGES}"
    )


def validate_summary_text(text: str) -> None:
  """요약할 텍스트의 유효성을 검사합니다."""
  
  if not text or not text.strip():
    raise HTTPException(status_code=400, detail="요약할 텍스트가 비어있습니다.")
  
  # 모든 길이 제한 제거 - 빈 텍스트만 검증


def validate_summary_parameters(language: str = None) -> None:
  """요약 매개변수의 유효성을 검사합니다."""
  
  if language is not None:
    valid_summary_languages = ["ko", "en", "ja", "zh"]
    if language not in valid_summary_languages:
      raise HTTPException(
          status_code=400,
          detail=f"지원하지 않는 요약 언어입니다. 사용 가능한 언어: {valid_summary_languages}"
      )


def validate_voice_order_result(order_info: dict) -> None:
  from config.naver_stt_settings import settings

  # 메뉴 신뢰도 검사
  menu_similarity = order_info.get("menu", {}).get("similarity", 0.0)
  if menu_similarity < settings.VOICE_ORDER_CONFIDENCE_THRESHOLD:
    raise VoiceOrderException(
        f"메뉴를 정확히 인식하지 못했습니다. (신뢰도: {menu_similarity:.2f}) "
        "다시 명확하게 말씀해주세요.",
        code="LOW_MENU_CONFIDENCE"
    )

  # 수량 검사
  quantity = order_info.get("quantity", 0)
  if quantity <= 0 or quantity > 99:
    raise VoiceOrderException(
        "잘못된 수량입니다. 1개부터 99개까지 주문 가능합니다.",
        code="INVALID_QUANTITY"
    )


def handle_voice_order_errors(error: Exception) -> JSONResponse:
  if isinstance(error, VoiceOrderException):
    return JSONResponse(
        status_code=400,
        content={
          "success": False,
          "error": error.message,
          "code": error.code
        }
    )
  elif isinstance(error, HTTPException):
    return JSONResponse(
        status_code=error.status_code,
        content={
          "success": False,
          "error": error.detail,
          "code": "HTTP_EXCEPTION"
        }
    )
  else:
    logger.error(f"예상치 못한 오류: {str(error)}")
    return JSONResponse(
        status_code=500,
        content={
          "success": False,
          "error": "서버 내부 오류가 발생했습니다.",
          "code": "INTERNAL_ERROR"
        }
    )


def handle_summary_errors(error: Exception) -> JSONResponse:
  """요약 관련 오류를 처리합니다."""
  if isinstance(error, SummaryException):
    return JSONResponse(
        status_code=400,
        content={
          "success": False,
          "error": error.message,
          "code": error.code
        }
    )
  elif isinstance(error, HTTPException):
    return JSONResponse(
        status_code=error.status_code,
        content={
          "success": False,
          "error": error.detail,
          "code": "HTTP_EXCEPTION"
        }
    )
  else:
    logger.error(f"요약 처리 중 예상치 못한 오류: {str(error)}")
    return JSONResponse(
        status_code=500,
        content={
          "success": False,
          "error": "요약 처리 중 서버 내부 오류가 발생했습니다.",
          "code": "SUMMARY_INTERNAL_ERROR"
        }
    )
