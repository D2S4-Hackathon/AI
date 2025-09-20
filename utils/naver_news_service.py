import requests
from config.news_settings import news_settings  # ✅ 새 설정 import

def search_naver_news(keyword: str, display: int = 4) -> list:
    """
    네이버 뉴스 검색 API 호출 (Naver Developers)
    """
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": news_settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": news_settings.NAVER_CLIENT_SECRET,
    }
    params = {"query": keyword, "display": display, "sort": "sim"}

    res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        data = res.json()
        articles = []
        for item in data.get("items", []):
            articles.append({
                "title": item["title"].replace("<b>", "").replace("</b>", ""),
                "url": item["link"]
            })
        return articles
    else:
        print("❌ 네이버 뉴스 API 호출 실패:", res.status_code, res.text)
        return []
