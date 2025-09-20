from typing import List, Optional
from models.content_model import Link
from services.openai_service import OpenAIService  # OpenAIService 있는 파일 import
import openai
from utils.link_utils import find_best_link
from utils.redis_utils import save_pending_query

import json
from typing import List
from utils.redis_utils import r
import uuid

# 전역 저장소 (데모용)
current_text: Optional[str] = None
current_links: List[Link] = []

openai_service = OpenAIService()

# 전역변수로 context 불러오기
# def load_content(inner_text: str, links: List[Link]):
#     global current_text, current_links
#     current_text = inner_text
#     current_links = links
#     return {"message": "Content loaded successfully", "links_count": len(current_links)}

def load_content(inner_text: str, links: List[Link], expire: int = 3600):
    session_id = str(uuid.uuid4())

    key = f"context:{session_id}"

    context_data = {
        "inner_text": inner_text,
        "links": [link.dict() for link in links]  # Link Pydantic 모델을 dict로 변환
    }

    r.setex(key, expire, json.dumps(context_data, ensure_ascii=False))
    return {
        "status": "success",           # 처리 상태
        "context_session_id": session_id,      # 반드시 반환
        "links_count": len(links)      # 저장된 링크 개수
    }

# redis를 context로 불러오는 메소드
def get_content(session_id: str) -> dict:
    key = f"context:{session_id}"
    data = r.get(key)
    if not data:
        return {}

    return json.loads(data)

def handle_query(session_id:str, query: str):
    # 전역변수로 불로오는 방식
    # global current_text, current_links
    #
    # if current_text is None:
    #     return {"error": "No content loaded yet"}

    context = get_content(session_id)
    if not context or "inner_text" not in context:
        return {"error": "No content loaded yet"}

    inner_text: str = context["inner_text"]                         # <-- 수정 포인트
    link_dicts = context.get("links", [])
    links: List[Link] = [
        (ld if isinstance(ld, Link) else Link(**ld)) for ld in link_dicts
    ]


    # 1) 이동 의도 판단: "보여줘"라는 단어 포함 여부
    if "보여줘" in query:
        # best_link = find_best_link(query, current_links)
        best_link = find_best_link(query, links)
        if best_link:
            return {
                "status" : "success",
                # "type": "navigation",
                "response": f"{best_link.text} 페이지로 이동합니다.",
                "url": best_link.url
            }
        return {
            "status": "success",
            # "type": "navigation",
            "response": "이동할 링크가 없습니다."
        }

    # 2) 이동 의도가 아니면 GPT로 문서 기반 답변
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 사용자가 제공한 문서를 기반으로만 답해야 한다. "
                    "사용자가 본문에 없는 내용을 추천해달라고 하거나, 알려달라고 요청하는 경우에도 본문에 없는 내용은 절대 말하지 마."
                    "본문 안에 존재하는 내용일 경우에만 필요 시 간단히 요약해서 대답해줘."
                    "문서에 없는 내용은 '본문에는 없습니다. 해당 내용에 대해 찾아드릴까요? 네/아니요로 대답해주세요.' 라고 반드시 답해라."
                )
            },
            {
                "role": "user",
                "content": (
                    f"다음은 사용자가 제공한 문서입니다:\n\n"
                    # f"{current_text}\n\n"
                    f"{inner_text}\n\n"
                    f"이 문서를 참고해서, 사용자의 질문에 답해줘.\n\n"
                    f"질문: {query}"
                )
            }
        ]
    )

    answer = response.choices[0].message.content

    # 3) "본문에는 없습니다" → pending_query 저장
    if "해당 내용에 대해 찾아" in answer:
        session_id = save_pending_query(query)  # Redis에 저장
        return {
            "status": "success",
            # "type": "summary",
            "response": "본문에는 없습니다. 해당 내용에 대해 찾아드릴까요? 네/아니요로 대답해주세요.",
            "pending_session_id": session_id
        }

    return {
        "status": "success",
        # "type": "summary",
        "response": answer
    }
