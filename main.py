from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.naver_stt_settings import settings, logger
from routers import content_router, yesno_router, news_router

# 라우터 임포트
from routers import stt
try:
    from routers import summary
    HAS_SUMMARY = True
except Exception as _e:
    logger.warning(f"summary 라우터를 불러오지 못했습니다: {_e}")
    HAS_SUMMARY = False

try:
    from routers import health
    HAS_HEALTH = True
except Exception as _e:
    logger.warning(f"health 라우터를 불러오지 못했습니다: {_e}")
    HAS_HEALTH = False

app = FastAPI(
    title="네이버 클로바 STT & OpenAI 요약 API",
    description="음성 인식 및 텍스트 요약 서비스",
    version="2.0.0",
    docs_url="/swagger-ui",
    redoc_url="/redoc",
)

cors_origins = getattr(settings, "CORS_ORIGINS", ["*"])
if isinstance(cors_origins, str):
    cors_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(stt.router)
app.include_router(content_router.router)
app.include_router(yesno_router.router)
app.include_router(news_router.router)
if HAS_SUMMARY:
    app.include_router(summary.router)
if HAS_HEALTH:
    app.include_router(health.router)

# 루트 핑
@app.get("/")
def ping():
    return {
        "status": "ok", 
        "service": "naver-stt-openai-summary", 
        "version": "2.0.0",
        "features": ["STT", "Summary"]
    }

logger.info("FastAPI 애플리케이션이 초기화되었습니다.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
