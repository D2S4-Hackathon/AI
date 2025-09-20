# ====== Build stage: wheel로 의존성 준비 ======
FROM python:3.12-slim AS builder
WORKDIR /app

# 빌드 도구 설치 (네이티브 의존성 대비)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
 && rm -rf /var/lib/apt/lists/*

# 의존성 캐시 최적화: 먼저 requirements만 복사
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# ====== Runtime stage: 얇은 이미지 ======
FROM python:3.12-slim
WORKDIR /app

ENV TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# curl은 헬스체크에 사용
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# wheel 설치
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# 앱 소스 복사 (프로젝트 루트 전체)
COPY . .

# 비루트 사용자
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

