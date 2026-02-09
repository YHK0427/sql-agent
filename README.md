# 🔍 Glass-Box SQL Agent

AI 기반 투명한 SQL 분석 플랫폼 - LLM을 활용한 자연어 기반 데이터베이스 쿼리 도구

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📌 프로젝트 개요

Glass-Box SQL Agent는 "투명성(Transparency)"을 핵심 가치로 하는 AI 기반 SQL 쿼리 생성 도구입니다. 
일반적인 블랙박스 AI와 달리, LLM의 사고 과정(Chain-of-Thought)과 생성된 SQL을 모두 공개하여 사용자가 결과를 검증하고 신뢰할 수 있도록 설계되었습니다.
개발직군이 아닌 타 마케팅 직군 같은 데이터를 다루어야만 하는 부서에서 어렵지 않게 sql을 모르더라고 데이터를 다룰 수 있게 해줍니다.

### 🎯 핵심 기능

- 🤖 자연어 → SQL 변환: Google Gemini를 활용한 정확한 쿼리 생성
- 🎛️ 다중 모델 지원: gemini-2.0-flash, gemini-2.5-flash 등 모델 선택 가능
- 📊 스키마 기반 분석: 동적 스키마 주입으로 환각(Hallucination) 최소화
- ⚡ 스마트 캐싱: 스키마 분석 결과 캐싱으로 토큰 절약 (DB 변경 시 자동 재분석)
- 💡 인텔리전트 추천: DB 구조를 분석해 유용한 질문 자동 제안
- 👁️ 투명한 프로세스: AI의 추론 과정과 생성된 SQL 실시간 공개
- 🛡️ Human-in-the-Loop: 사용자 검증 후 실행하는 안전장치
- 📜 쿼리 히스토리: 과거 질문/SQL 저장 및 재사용 + 북마크 기능
- 📥 데이터 내보내기: CSV/Excel 형식 지원
- 🗂️ 스키마 시각화: Mermaid.js 기반 ER 다이어그램 (확대 뷰)

---

## 🏗️ 시스템 아키텍처
```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  HTML/CSS/JS (Vanilla) + Pretendard Font + Mermaid.js       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│                         Flask API                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Schema       │  │ Query        │  │ History      │      │
│  │ Analyzer     │  │ Generator    │  │ Manager      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         LLM Layer                            │
│                    Google Gemini API                         │
│              (Prompt Engineering + RAG)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  SQLite (User DBs) + query_history.db (Metadata)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 시작하기

### 1. 필수 요구사항

- Python 3.8 이상
- Google Gemini API Key ([발급받기](https://makersuite.google.com/app/apikey))

### 2. 설치
```bash
# 저장소 클론
git clone https://github.com/yourusername/glass-box-sql-agent.git
cd glass-box-sql-agent

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

`.env` 파일 생성:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. 샘플 데이터베이스 생성
```bash
cd database
python init_dbs.py
python init_history.py
cd ..
```

### 5. 서버 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

---

## 📂 프로젝트 구조
```
sql-agent/
├── app.py                    # Flask 메인 애플리케이션
├── config.py                 # DB 설정 및 경로 관리
├── requirements.txt          # 의존성 패키지
├── .env                      # 환경 변수 (API 키)
│
├── database/
│   ├── init_dbs.py          # 샘플 DB 생성 스크립트
│   ├── init_history.py      # 히스토리 DB 초기화
│   ├── metadata.json        # DB 메타데이터
│   ├── ecommerce.db         # 전자상거래 샘플 DB
│   ├── hr_management.db     # 인사관리 샘플 DB
│   ├── finance.db           # 재무 샘플 DB
│   └── query_history.db     # 쿼리 히스토리 저장소
│
├── utils/
│   ├── gemini_client.py     # Gemini API 래퍼
│   ├── schema_analyzer.py   # 스키마 분석 및 다이어그램 생성
│   └── query_generator.py   # SQL 생성 및 실행 로직
│
├── templates/
│   ├── base.html            # 기본 레이아웃
│   ├── home.html            # DB 선택 화면
│   └── dashboard.html       # 쿼리 대시보드
│
└── static/
    ├── css/
    │   └── style.css        # 커스텀 스타일 (다크 테마)
    └── js/
        ├── main.js          # 공통 유틸리티
        └── dashboard.js     # 대시보드 로직
```

---

## 💡 주요 기술 스택

| 분류 | 기술 |
|------|------|
| **Backend** | Flask, Python 3.8+ |
| **Database** | SQLite |
| **LLM** | Google Gemini API (Multi-Model) |
| **Caching** | JSON-based Schema Cache |
| **Frontend** | Vanilla JavaScript, Pretendard Font |
| **Visualization** | Mermaid.js |
| **Export** | openpyxl (Excel), csv (CSV) |

---

## 🎨 주요 화면

### 1. 홈 화면
- 다중 데이터베이스 관리
- DB 추가/삭제 기능
- 모던 다크 테마 UI

### 2. 대시보드
- 좌측 사이드바: 쿼리 히스토리
- 메인 영역:
  - DB 구조 자동 분석
  - AI 추천 질문
  - 자연어 입력 → SQL 생성
  - 결과 테이블 + 내보내기

### 3. Glass-Box 특징
```
사용자 질문: "VIP 고객들의 평균 구매 금액은?"
            ↓
💭 AI 사고 과정:
"Users 테이블에서 tier='VIP'인 고객을 필터링하고,
Orders 테이블과 JOIN하여 평균 금액을 계산합니다."
            ↓
📝 생성된 SQL:
SELECT AVG(o.amount)
FROM Users u
JOIN Orders o ON u.user_id = o.user_id
WHERE u.tier = 'VIP'
            ↓
[사용자 검증 후 실행 버튼 클릭]
            ↓
📊 결과: 1,250,000원
```

---

## 🔧 설정 및 커스터마이징

### DB 추가 방법

1. UI에서 "새 데이터베이스" 카드 클릭
2. DB Key, 이름, 설명, 아이콘 입력
3. SQLite 파일 자동 생성됨
4. 테이블 생성은 별도로 진행

### 프롬프트 엔지니어링

`utils/schema_analyzer.py`와 `utils/query_generator.py`에서 프롬프트 커스터마이징 가능:
```python
# 예: SQL 생성 시스템 프롬프트
prompt = f"""
당신은 SQLite 전문가입니다. 
아래 스키마를 참고하여 질문에 맞는 쿼리를 작성해주세요.

<스키마>
{schema_text}

<질문>
{user_question}
...
"""
```

---

## 📊 샘플 데이터베이스

### 1. E-Commerce DB
- 테이블: Users, Products, Orders
- 샘플 질문:
  - "지난 30일간 가장 많이 팔린 상품 TOP 5는?"
  - "VIP 고객의 평균 주문 금액은?"

### 2. HR Management DB
- 테이블: Employees, Departments, Salaries
- 샘플 질문:
  - "부서별 평균 연봉은?"
  - "입사한 지 3년 이상 된 직원 수는?"

### 3. Finance DB
- 테이블: Accounts, Transactions
- 샘플 질문:
  - "이번 달 총 지출은?"
  - "비용 항목별 합계는?"

---

## 🛠️ 개발 배경 및 학습 포인트

### LLMOps 관점
- 동적 스키마 주입: RAG의 기초 개념 적용
- Few-shot Learning: 프롬프트에 예시 포함으로 정확도 향상
- 출력 파싱: XML 태그 기반 구조화된 응답 처리

### 엔지니어링 관점
- 3-Tier Architecture: Presentation - Application - Data 분리
- RESTful API 설계: `/api/` 엔드포인트 표준화
- 상태 관리: SQLite 기반 히스토리 영구 저장

### UX/AX 관점
- 설명 가능한 AI(XAI): 사고 과정 공개로 신뢰성 확보
- Human-in-the-Loop: 실행 전 사용자 검증 단계 필수화
- 점진적 공개: 로딩 상태 → 결과 → 상세 정보 순차 표시

---

## 🚧 향후 개선 계획

- [ ] PostgreSQL, MySQL 등 다른 DBMS 지원
- [ ] 복잡한 쿼리 자동 최적화
- [ ] 쿼리 실행 계획(Explain) 시각화
- [ ] 사용자별 권한 관리 (Read-Only/Read-Write)
- [ ] WebSocket 기반 실시간 쿼리 스트리밍
- [ ] 차트 자동 생성 (Plotly, Chart.js)

---


## 👤 개발자

[Your Name]
- GitHub: [@YHK0427](https://github.com/YHK0427)
- Email: bleach10905@gmail.com

---

## 🙏 참고 자료

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/prompt-engineering)

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!


