# 🎙️ STT & 요약 서비스 (독립 실행)

네이버 클로바 STT와 OpenAI를 활용한 음성 인식 및 텍스트 요약 API 서비스입니다.

## ✨ 주요 기능

### 🔊 음성 인식 (STT)
- **네이버 클로바 STT API** 연동
- **다국어 지원**: 한국어, 영어, 일본어, 중국어
- **다양한 오디오 형식** 지원 (WAV, MP3, FLAC 등)
- **파일 크기 제한**: 10KB ~ 50MB

### 📝 텍스트 요약 (독립 서비스)
- **OpenAI GPT 모델** 활용
- **다국어 요약** 지원 (한국어, 영어, 일본어, 중국어)
- **커스텀 요약 길이** 설정 가능
- **압축률 정보** 제공

## 🛠️ 기술 스택

- **Framework**: FastAPI 0.104.1
- **Web Server**: Uvicorn 0.24.0
- **AI Services**: 
  - 네이버 클로바 STT API
  - OpenAI GPT API
- **Python**: 3.11+

## 📁 프로젝트 구조

```
AI/
├── config/                 # 설정 관리
│   ├── naver_stt_settings.py
│   └── __init__.py
├── core/                   # 핵심 기능
│   ├── common/
│   └── exceptions/
│       └── stt_exceptions.py
├── models/                 # 데이터 모델
│   ├── stt_models.py
│   └── __init__.py
├── routers/                # API 라우터
│   ├── stt.py             # STT 전용 라우터
│   ├── summary.py         # 요약 전용 라우터
│   ├── health.py          # 헬스체크
│   └── __init__.py
├── services/               # 비즈니스 로직
│   ├── naver_stt_service.py
│   ├── openai_service.py
│   └── __init__.py
├── main.py                # FastAPI 앱 진입점
├── requirements.txt       # 패키지 의존성
├── .env.example          # 환경변수 예시
└── test_main.http        # API 테스트 파일
```

## 🚀 빠른 시작

### 1. 저장소 클론 및 의존성 설치

```bash
git clone <repository-url>
cd AI
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 API 키를 설정하세요.

```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
# 네이버 클로바 STT API (필수)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# OpenAI API (요약 기능 사용 시 필수)
OPENAI_API_KEY=your_openai_api_key

# CORS 설정
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 3. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면 다음 주소에서 접근 가능합니다:
- **API 문서**: http://localhost:8000/swagger-ui
- **ReDoc**: http://localhost:8000/redoc
- **서비스 상태**: http://localhost:8000/health

## 📖 API 사용법

### 🎯 주요 엔드포인트

#### 1. 음성 인식 (STT)
```bash
POST /stt/
```
- **파라미터**: 
  - `audio_file`: 음성 파일 (multipart/form-data)
  - `lang`: 언어 설정 (Kor/Eng/Jpn/Chn)

#### 2. 텍스트 요약
```bash
POST /summary/text
```
- **Body (JSON)**:
```json
{
  "text": "요약할 텍스트",
  "max_length": 500,
  "language": "ko"
}
```

#### 3. 서비스 상태 확인
```bash
GET /health                    # 전체 서비스 상태
GET /summary/status           # 요약 서비스 상태
GET /languages               # 지원 언어 목록
```

### 📋 응답 예시

#### STT 응답
```json
{
  "success": true,
  "text": "안녕하세요. 음성 인식 테스트입니다.",
  "confidence": 0.95
}
```

#### 요약 응답
```json
{
  "success": true,
  "original_text": "원본 텍스트...",
  "summary": "요약된 텍스트...",
  "original_length": 500,
  "summary_length": 150,
  "compression_ratio": 70.0
}
```

## ⚙️ 설정 옵션

### 파일 크기 제한
- **최소**: 10KB (최소 1초 음성)
- **최대**: 50MB

### 텍스트 길이 제한
- **요약 최소 길이**: 100자
- **요약 최대 길이**: 2,000자
- **처리 가능 최대 텍스트**: 10,000자

### 지원 언어
- **STT**: 한국어(Kor), 영어(Eng), 일본어(Jpn), 중국어(Chn)
- **요약**: 한국어(ko), 영어(en), 일본어(ja), 중국어(zh)

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!
