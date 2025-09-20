import os
from dotenv import load_dotenv

load_dotenv()

class NewsSettings:
    def __init__(self):
        self.NAVER_CLIENT_ID: str = os.getenv("NAVER_NEWS_CLIENT_ID")
        self.NAVER_CLIENT_SECRET: str = os.getenv("NAVER_NEWS_CLIENT_SECRET")

        if not self.NAVER_CLIENT_ID or not self.NAVER_CLIENT_SECRET:
            raise ValueError("❌ NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env에 설정해주세요.")

# 전역 인스턴스
news_settings = NewsSettings()
