# routers/news_router.py
from fastapi import APIRouter, HTTPException
from services.news_service import get_selected_news

router = APIRouter(prefix="/news", tags=["News"])

@router.post("/select")
def select_news(news_session_id: str, query: str):
    # 저장된 뉴스 세션에서 사용자의 query(예: '첫 번째 기사')에 맞는 기사 반환
    article = get_selected_news(news_session_id, query)

    if not article:
        raise HTTPException(status_code=404, detail="뉴스 세션이 만료되었거나 기사를 찾을 수 없습니다.")

    return {
        "type": "navigation",
        "response": f"선택하신 기사 → '{article['title']}'",
        "url": article["url"]
    }
