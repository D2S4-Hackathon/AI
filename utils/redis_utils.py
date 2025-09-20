import uuid
import redis
import json

# Redis 클라이언트 초기화
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# pending query 저장 (TTL 기본 300초 = 5분)
def save_pending_query(query: str, ttl: int = 300) -> str:
    session_id = str(uuid.uuid4())  # 고유 세션 ID 생성
    data = {"query": query}
    r.setex(f"pending:{session_id}", ttl, json.dumps(data))
    return session_id

# pending query 불러오기
def get_pending_query(session_id: str):
    raw = r.get(f"pending:{session_id}")
    return json.loads(raw) if raw else None

# pending query 삭제
def clear_pending_query(session_id: str):
    r.delete(f"pending:{session_id}")
