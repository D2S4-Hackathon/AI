from fastapi import APIRouter
from pydantic import BaseModel
from services.yesno_service import handle_yes_no
from typing import Optional

router = APIRouter(prefix="/content", tags=["Content"])

class YesNoRequest(BaseModel):
    answer: str

@router.post("/yesno")
def yesno_endpoint(    pending_session_id: str, context_session_id: str, request: YesNoRequest):
    # 사용자가 '네/아니요'로 대답했을 때 후속 처리
    result = handle_yes_no(request.answer, pending_session_id, context_session_id)
    return result
