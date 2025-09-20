# services/news_service.py
import json
from utils.redis_utils import r

def save_news_session(news_session_id: str, articles: list, expire: int = 3600):
    # 뉴스 기사 리스트를 Redis에 저장
    key = f"news:{news_session_id}"
    r.setex(key, expire, json.dumps(articles, ensure_ascii=False))

def get_selected_news(news_session_id: str, user_query: str):
    # Redis에서 뉴스 기사 불러와서 '첫 번째', '두 번째' 같은 순서 입력 기반으로 기사 반환
    key = f"news:{news_session_id}"
    raw_data = r.get(key)
    if not raw_data:
        return None

    articles = json.loads(raw_data)

    # 순서 매칭 (첫 번째, 두 번째, 세 번째, 네 번째)
    order_map = {
        "첫번째": 0, "첫 번째": 0,
        "두번째": 1, "두 번째": 1,
        "세번째": 2, "세 번째": 2,
        "네번째": 3, "네 번째": 3,
    }

    for k, idx in order_map.items():
        if k in user_query and idx < len(articles):
            return articles[idx]

    # fallback → 첫 번째 기사 반환
    return articles[0] if articles else None
