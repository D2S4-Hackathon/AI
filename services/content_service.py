from typing import List, Optional
from models.content_model import Link
from services.openai_service import OpenAIService  # OpenAIService 있는 파일 import
import openai

# 전역 저장소 (데모용)
current_text: Optional[str] = None
current_links: List[Link] = []

openai_service = OpenAIService()

def load_content(inner_text: str, links: List[Link]):
    global current_text, current_links
    current_text = inner_text
    current_links = links
    return {"message": "Content loaded successfully", "links_count": len(current_links)}

def handle_query(query: str):
    global current_text, current_links

    if current_text is None:
        return {"error": "No content loaded yet"}

    # 1) 이동 의도 판단: "보여줘"라는 단어 포함 여부
    if "보여줘" in query:
        for link in current_links:
            if link.text in query:
                return {
                    "type": "navigation",
                    "response": f"{link.text} 페이지로 이동합니다.",
                    "url": link.url
                }
        # 링크 못 찾았을 경우
        return {
            "type": "navigation",
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
                    "문서에 없는 내용은 모른다고 답해라. "
                    "필요하면 간단히 요약해서 알려줘."
                )
            },
            {
                "role": "user",
                "content": (
                    f"다음은 사용자가 제공한 문서입니다:\n\n"
                    f"{current_text}\n\n"
                    f"이 문서를 참고해서, 사용자의 질문에 답해줘.\n\n"
                    f"질문: {query}"
                )
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "type": "summary",
        "response": answer
    }
