from typing import List, Optional
from rapidfuzz import process
from models.content_model import Link

def find_best_link(query: str, links: List[Link]) -> Optional[Link]:
    candidates = {link.text: link for link in links}
    best_match, score, _ = process.extractOne(query, candidates.keys())
    if score > 60:  # 유사도 임계값
        return candidates[best_match]
    return None