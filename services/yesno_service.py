import openai
import json
from utils.redis_utils import get_pending_query, clear_pending_query, r
from utils.naver_news_service import search_naver_news
import uuid

def classify_and_expand(original_query: str, context: str) -> dict:

    prompt = (
        "너는 사용자의 질문을 'term' 또는 'article'로 분류해야 한다.\n"
        "- 특정 개념, 용어, 정의, 의미 → 'term'\n"
        "- 관련 기사, 뉴스, 사건, 소식 → 'article'\n"
        "분류 후 반드시 핵심 검색어(keyword)도 뽑아라.\n"
        "출력 형식:\n"
        "{ \"category\": \"term\", \"keyword\": \"검색 키워드\" }\n"
        "또는\n"
        "{ \"category\": \"article\", \"keyword\": \"검색 키워드\" }\n"
        "만약 'term'이면 context는 무시하고 질문에서만 keyword를 뽑아라.\n"
        "만약 'article'이면,  context 내용 중 가장 주된 내용의 단어를 keyword로 뽑아라."
        "만약 사용자가 '이 기사'라고 말하면, 반드시 제공된 context(본문)을 '이 기사'로 간주하라.\n"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"질문: {original_query}\n\n본문: {context}"}
        ]
    )
    return json.loads(response.choices[0].message.content.strip())


def handle_yes_no(answer: str, pending_session_id: str, context_session_id: str):
    # "아니요" 처리
    if answer.strip() == "아니요":
        clear_pending_query(pending_session_id)
        return {
            "status": "success",
            # "type": "info",
            "response": "네, 알겠습니다."
        }

    # "네" 처리
    if answer.strip() == "네":
        pending = get_pending_query(pending_session_id)

        if not pending:
            return {
                "type": "error",
                "response": "이전 질문을 찾을 수 없습니다. 다시 질문해주세요."
            }

        original_query = pending["query"]
        # clear_pending_query(session_id)  # 사용 후 삭제 - 추후추가

        # Redis에서 context 불러오기 (별도의 context 세션 ID 사용)
        raw_context = r.get(f"context:{context_session_id}")
        effective_context = ""
        if raw_context:
            try:
                context_data = json.loads(raw_context)
                effective_context = context_data.get("inner_text", "")
            except json.JSONDecodeError:
                effective_context = ""

        # Redis 기반 context 사용
        result = classify_and_expand(original_query, effective_context)

        category = result.get("category")
        keyword = result.get("keyword", original_query)

        # 클린 단어 하기 전 코드
        # if category == "term":
        #     return {
        #         "type": "navigation",
        #         "response": f"'{keyword}'에 대한 어학사전 링크를 보여드립니다.",
        #         "url": f"https://dict.naver.com/search.dict?query={keyword}"
        #     }

        if category == "term":
            clean_keyword = keyword.split()[0]
            return {
                "status": "success",
                # "type": "navigation",
                "response": f"'{clean_keyword}'에 대한 어학사전 링크를 보여드립니다.",
                "url": f"https://dict.naver.com/search.dict?query={clean_keyword}"
            }

        if category == "article":
            articles = search_naver_news(keyword, display=4)

            if not articles:
                return {
                    "type": "articles",
                    "response": f"'{keyword}' 관련 뉴스를 보여드리려 했으나 찾지 못했습니다.",
                    "articles": []
                }

            news_session_id = str(uuid.uuid4())  # 새 ID 발급
            news_key = f"news:{news_session_id}"
            r.setex(news_key, 3600, json.dumps(articles, ensure_ascii=False))

            return {
                "status": "success",
                # "type": "articles",
                "response": f"'{keyword}' 관련 뉴스를 보여드립니다.",
                "news_session_id": news_session_id,  # 프론트로 전달
                "articles": articles
            }

        # fallback
        return {
            "type": "error",
            "response": "질문을 분류하지 못했습니다. 다시 시도해주세요."
        }

    # "네/아니요" 외 입력
    return {
        "type": "error",
        "response": "네/아니요로만 대답해주세요."
    }
