from fastapi import APIRouter
from pydantic import BaseModel
from services.yesno_service import handle_yes_no
from typing import Optional

router = APIRouter(prefix="/content", tags=["Content"])

class YesNoRequest(BaseModel):
    answer: str
    session_id: str
    context: Optional[str] = None

@router.post("/yesno")
def yesno_endpoint(request: YesNoRequest):
    """
    사용자가 '네/아니요'로 대답했을 때 후속 처리
    """
    result = handle_yes_no(request.answer, request.session_id, request.context)
    return result
