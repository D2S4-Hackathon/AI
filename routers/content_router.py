from fastapi import APIRouter, HTTPException
from models.content_model import ContentRequest, UserQuery
from services import content_service


router = APIRouter(prefix="/content", tags=["Content"])

@router.post("/load")
def load_content(content: ContentRequest):
    return content_service.load_content(content.inner_text, content.links)

@router.post("/ask")
def ask(context_session_id:str, query: UserQuery):
    result = content_service.handle_query(context_session_id, query.query)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
