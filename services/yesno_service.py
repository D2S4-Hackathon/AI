import openai
from utils.redis_utils import get_pending_query, clear_pending_query
import json
from services.content_service import current_text

def generate_related_articles_with_gpt(keyword: str, count: int = 4) -> list:
    """GPT에게 키워드를 주고 관련 뉴스 3~4개를 JSON으로 생성"""
    prompt = (
        f"'{keyword}'와 관련된 최신 뉴스를 {count}개 찾아서 알려줘.\n"
        "- 반드시 JSON 배열 형식으로만 출력해야 한다.\n"
        "- 출력 예시:\n"
        "[\n"
        "  {\"title\": \"기사 제목1\", \"url\": \"https://news.naver.com/1\"},\n"
        "  {\"title\": \"기사 제목2\", \"url\": \"https://news.naver.com/2\"}\n"
        "]\n"
        "- url은 실제 뉴스 기사처럼 보이는 형식(예: https://news.naver.com/...)으로 만들어야 한다.\n"
        "- 절대 설명 문장이나 추가 텍스트는 쓰지 마라. JSON만 출력."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 뉴스 추천 시스템이다."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("❌ JSON 파싱 실패, GPT 응답:", raw_output)
        return []



# key_word 뽑아내기 전 코드
# def classify_query(original_query: str) -> str:
    # response = openai.ChatCompletion.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": (
    #                 "너는 사용자의 질문을 'term' 또는 'article' 두 가지로만 분류해야 한다.\n"
    #                 "- 특정 개념, 용어, 정의, 의미를 묻는 질문 → 'term'\n"
    #                 "- 관련 기사, 뉴스, 보도, 사건, 소식 등을 묻는 질문 → 'article'\n"
    #
    #                 "분류 후 반드시 핵심 검색어(keyword)도 뽑아라.\n"
    #                 "출력 형식:\n"
    #                 "{ \"category\": \"term\", \"keyword\": \"검색 키워드\" }\n"
    #                 "또는\n"
    #                 "{ \"category\": \"article\", \"keyword\": \"검색 키워드\" }"
    #                 "만약 'term'이면 context는 무시하고 질문에서만 keyword를 뽑아라.\n"
    #                 "만약 'article'이면 질문과 context를 모두 고려해서 keyword를 뽑아라."
    #
    #                 "그 외는 무조건 가장 가까운 걸로 골라라.\n"
    #                 # "출력은 반드시 term 또는 article 중 하나만 해라."
    #             )
    #         },
    #         {
    #             "role": "user",
    #             "content": original_query
    #         }
    #     ]
    # )

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
        "만약 'article'이면 질문과 context를 모두 고려해서 keyword를 뽑아라."
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


def handle_yes_no(answer: str, session_id: str, context: str):
    # "아니요" 처리
    if answer.strip() == "아니요":
        clear_pending_query(session_id)
        return {
            "type": "info",
            "response": "네, 알겠습니다. 다른 질문을 해주세요."
        }

    # "네" 처리
    if answer.strip() == "네":
        pending = get_pending_query(session_id)
        if not pending:
            return {
                "type": "error",
                "response": "이전 질문을 찾을 수 없습니다. 다시 질문해주세요."
            }

        original_query = pending["query"]
        # clear_pending_query(session_id)  # 사용 후 삭제 - 추후추가

        # # GPT로 분류
        # category = classify_query(original_query)
        #
        # if category == "term":
        #     return {
        #         "type": "navigation",
        #         "response": f"'{original_query}'에 대한 어학사전 링크를 보여드립니다.",
        #         "url": f"https://dict.naver.com/search.dict?query={original_query}"
        #     }
        #
        # if category == "article":
        #     return {
        #         "type": "navigation",
        #         "response": f"'{original_query}' 관련 뉴스를 보여드립니다.",
        #         "url": f"https://search.naver.com/search.naver?where=news&query={original_query}"
        #     }

        # ✅ context가 없으면 전역 current_text(기사 본문) 사용
        effective_context = current_text

        # GPT로 분류 + keyword 추출
        # result = classify_and_expand(original_query, context)
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
                "type": "navigation",
                "response": f"'{clean_keyword}'에 대한 어학사전 링크를 보여드립니다.",
                "url": f"https://dict.naver.com/search.dict?query={clean_keyword}"
            }

        # if category == "article":
        #     return {
        #         "type": "navigation",
        #         "response": f"'{keyword}' 관련 뉴스를 보여드립니다.",
        #         "url": f"https://search.naver.com/search.naver?where=news&query={keyword}"
        #     }

        if category == "article":
            articles = generate_related_articles_with_gpt(keyword, count=4)

            if not articles:
                return {
                    "type": "articles",
                    "response": f"'{keyword}' 관련 뉴스를 보여드리려 했으나 찾지 못했습니다.",
                    "articles": []
                }

            return {
                "type": "articles",
                "response": f"'{keyword}' 관련 뉴스를 보여드립니다.",
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
