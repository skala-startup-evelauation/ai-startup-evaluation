# 🚀 AI-startup-evaluation

AI 스타트업 투자 판단을 지원하는 멀티에이전트 시스템입니다.  
시장성, 기술력, 경쟁력, 창업자 역량을 종합적으로 평가하여 투자 추천 여부를 자동으로 분석하고 보고서를 생성합니다.

---

## 📂 프로젝트 구조

```bash
project_root/
├── src/
│   ├── common/                      # 공통 모델·유틸
│   │   ├── __init__.py
│   │   ├── models.py                # BaseModel 정의 (FundingRound, MarketMetrics 등)
│   │   ├── schema.py                # StateGraph 스키마 타입 (pydantic BaseModel)
│   │   └── utils.py                 # HTTP 요청, RAG 처리, 로깅 등
│   │
│   ├── agents/                      # 에이전트별 구현
│   │   ├── startup_search/          # 🔍 스타트업 탐색 에이전트
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # FIELDS_TO_EXTRACT, 검색 파라미터 정의
│   │   │   ├── state_models.py      # 입력/출력 BaseModel (Input, Output 정의)
│   │   │   ├── graph_builder.py     # StateGraph 빌더(노드·엣지 정의)
│   │   │   └── executor.py          # graph.invoke 호출부(main 함수)
│   │   │
│   │   ├── tech_summary/            # 🗜️ 기술 요약 에이전트
│   │   │   ├── __init__.py
│   │   │   ├── state_models.py
│   │   │   ├── graph_builder.py
│   │   │   └── executor.py
│   │   │
│   │   ├── market_evaluation/       # 📊 시장성 평가 에이전트
│   │   │   ├── __init__.py
│   │   │   ├── state_models.py
│   │   │   ├── graph_builder.py
│   │   │   └── executor.py
│   │   │
│   │   ├── founder_evaluation/      # 👤 창업자 평가 에이전트
│   │   │   └── ...
│   │   │
│   │   ├── investment_decision/     # 🧮 투자 판단 에이전트
│   │   │   └── ...
│   │   │
│   │   └── report_generation/       # 📝 보고서 생성 에이전트
│   │       └── ...
│   │
│   └── main.py                      # 전체 파이프라인 orchestration
│
├── tests/                           # 유닛테스트
│   └── agents/
│       └── startup_search/
│           └── test_graph.py
│
├── requirements.txt
└── README.md

```

---

## 🛠️ 설치 및 실행

### 1. Python 및 패키지 설치

Python 3.11 이상 필요

```bash
python -m venv venv
source venv/bin/activate   # (Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일 작성

```bash
OPENAI_API_KEY=your-openai-api-key
VECTOR_DB_PATH=./vector_db
HOST=0.0.0.0
PORT=8001
DEBUG=true
```

### 3. FastAPI 서버 실행

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

---

# 📋 목차

1. [Agent 정의](#-agent-정의)
2. [RAG 문서 정의](#-rag-문서-정의)
3. [전체 흐름 요약](#-전체-흐름-요약)

---

## 🧠 Agent 정의

| **에이전트** | task | **벡터디비여부** | **내용** |
| :--- | :--- | :--- | :--- |
| 🔍 스타트업 탐색 에이전트 | 유명 AI 스타트업 수집 | ❌ | 웹서치, 투자 리포트 활용 |
| 🗜️ 기술 요약 에이전트 | 스타트업 핵심 기술 요약 | ❌ | 홈페이지, 논문 기반 요약 |
| 📊 시장성 평가 에이전트 | 시장 규모/성장성 분석 | ✅ | 시장 리포트 기반 분석 |
| 👤 창업자 평가 에이전트 | 창업자 이력 및 리스크 평가 | ❌ | 웹 검색 기반 |
| 🥊 경쟁사 비교 에이전트 | 경쟁사 대비 차별성 분석 | ❌ | 산업 뉴스/DB 활용 |
| 🧮 투자 판단 에이전트 | 최종 투자 여부 결정 |✅ | 스코어 종합 및 리스크 반영 |
| 📝 보고서 생성 에이전트 | 보고서 자동 작성 | ❌ | 요약 결과 종합 서술 |

![ChatGPT Image 2025년 4월 30일 오후 04_09_03](https://github.com/user-attachments/assets/81e48d6d-8ae4-4afc-aa14-c2903dfe1cd1)

---

## 📑 RAG 문서 정의

| 카테고리 | 문서 예시 (한국 기준) | 목적 |
| --- | --- | --- |
| 산업/시장 리포트 | 한국정보통신진흥협회(KAIT), 한국AI학회, KOTRA, 산업연구원 | 시장 규모/성장성 분석 |
| 스타트업 데이터베이스 | K-Startup, THE VC, 로켓펀치 | 스타트업 투자 이력/기본정보 |
| 기술 논문/백서 | ETRI 논문, AI 백서 | 핵심 기술 파악 |
| 창업자 정보 | 로켓펀치, 언론 기사 | 창업자 역량 분석 |
| 산업 뉴스/인사이트 | 블로터, ZDNet, VentureBeat | 시장 트렌드 및 경쟁사 정보 |

---

# 🛤️ 전체 흐름 요약

```
📊 시장성 평가 (정형정보 추출)
    ↓
🔍 스타트업 탐색 (하이브리드 RAG)
    ↓
🗜️ 기술 요약 (멀티 문서 요약)
    ↓
👤 창업자 평가 (백그라운드 요약)
    ↓
🧮 투자 판단 (가중치 스코어링 + 리스크 반영)
    ↓
📝 보고서 생성 (구조화+자연어 서술)
```

---
## 1. 📊 시장성 평가 에이전트

(**"지표 추출형 Structured RAG" 사용**)

### 목적

- 해당 산업군의 시장 크기, 성장성 파악

### 사용할 RAG 문서

1.RE169_국내AI창업기업_비즈니스_현황분석 (3장, 5장만 파싱)
2.IF_Strategy24-03_글로벌_정부·민간_분야_AI_투자_동향_분석_최종(참고문헌빼고, 11페이지부터)
3.250130__startup-recipe_investment-report_24_v00190(전체)


### 방법 (RAG 설계)
문서 처리 파이프라인
PDF 로드 → 섹션 추출 → GPT 요약 → 청킹 → 벡터 DB 저장 → QA 시스템
핵심 컴포넌트
- 문서 로더 : PyMuPDFLoader
- 임베딩 모델 : sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 벡터 저장소 : Chroma DB
- 언어 모델 : GPT-4
- 검색 시스템 : MMR + Multi-Query Retriever
문서별 처리 방법
- IF_Strategy : <...> 형식의 섹션 구분
- RE169 : [표/그림 숫자-숫자] 형식의 섹션 구분
- StartupRecipe : 전체 텍스트 통합 처리
처리 단계
1. 섹션 추출
    - 문서 유형별 정규식 패턴 매칭
   - 제목과 내용 분리
2. 내용 요약
    - GPT-4를 활용한 섹션별 요약 생성
   - 3-4문장 길이의 핵심 내용 추출
3. 청킹 처리
    - 512 토큰 단위로 분할
   - 100 토큰 오버랩으로 문맥 유지
4. 벡터 DB 저장
   - 문서 임베딩 생성
   - Chroma DB에 영구 저장

✅ **RAG 핵심**:

- 비정형 리포트에서 **정형지표 추출** (Entity Extraction + Parsing)


# 2. 🔍 스타트업 탐색 에이전트

(**"멀티 소스 (thevc.kr 공시 정보 활용)**)

### 목적

- 입력 키워드/투자금에 맞는 스타트업 검색
- 단순 키워드 매칭이 아니라 "시장성 + 투자 가능성"을 함께 고려
- THE VC 엑셀 데이터와 실제 웹 페이지를 활용하여 유망 스타트업 탐색

### 방법 (RAG 설계)
1. **Branch 처리**
    - 투자금 데이터가 없는 경우 → 뉴스/리포트 RAG로만 추출
    - 투자금 있는 경우 → 조건 필터 후 선정
2. **Loop 처리**
    - sector 키워드 관련성 높은 스타트업 최소 20개 수집
    - 투자금 기준 필터 → 조건 만족 스타트업 5~10개로 좁힘 (다단계 loop)

1. ✅ get_company_links_by_category()
./thevc_invest_list.xlsx 파일의 1행(헤더)에서 sector 키워드에 해당하는 열을 찾음

해당 열에서 기업 이름(B열)과 하이퍼링크(URL)을 추출

예시 출력:

    {"company": "푸드테크코리아", "link": "https://thevc.kr/FoodTechKorea"},
    ...

2. ✅ build_thevc_prompt(company_name, link)
THE VC 기업 상세 페이지를 읽고 LLM이 추출할 JSON 필드를 명시

명세된 필드 리스트:

[
    "기업 이름", "설립연월", "상세정보", "대표자 정보", "경쟁사 리스트", "상장, 비상장 여부",
    "투자 라운드", "투자 유치 건수", "투자 금액", "임직원수", "회사 홈페이지",
    "제품/서비스 목록", "특허 개수", "등기 임원 수", "AI_관련기업여부", "AI_관련성_설명"
]
### 🌐 웹 탐색 방식 (Browser-Use 기반)
✅ browser_use를 이용한 실행 방식
Agent 생성


agent = Agent(task=prompt, llm=ChatOpenAI(...), browser=Browser(...))
LangChain LLM(gpt-4o)과 headless Chrome 조합

Prompt 기반 시뮬레이션 실행

history = await agent.run()
result = history.final_result()
결과 파싱 및 필터링

JSON으로 파싱

"AI_관련기업여부"가 True인 기업만 선별

기업 이름 → StartupSearchOutput 모델로 매핑

### 🔁 기타 세부처리

한 번에 5개씩 브라우저로 병렬 탐색 (batch)
기업 수가 50개 이상이면 30~35번째 기업부터 추출 (실행 속도 제한)
AI 관련 기업이 3~5개 발견되면 탐색 종료


# 3. 🗜️기술 요약 에이전트

(**"다큐먼트 매칭 + 집중 요약형 RAG" 사용**)

### 목적

- 스타트업 기술력 파악

### 방법 (RAG 설계)

1. **Branch 처리**
    - 홈페이지에 명시적 기술 설명 있으면 → 우선 추출
    - 없으면 논문이나 뉴스 기반으로 fallback
2. **Loop 처리**
    - 하나의 스타트업당 **최대 3개 자료**까지 요약
    - 다중 소스 합성 (Early Fusion) 후 요약
4. **요약 시 전략**
    - core_technology만 추출
    - strengths/weaknesses는 별도로 지시문(Prompt) 내 삽입해 강제 추출

# 4. 👤 창업자 평가 에이전트

(**"Background Summarization RAG" 사용**)

### 목적

- 창업자 경력, 성과, 위험요소 평가

### 사용할 RAG 문서

- LinkedIn 프로필
- 언론 인터뷰 기사 (한경, 조선비즈)

### 방법 (RAG 설계)

1. **Multi-source Background Retrieval**
    - founder_name + "경력", "프로필", "창업 경험" 키워드로 검색
2. **Branch 처리**
    - 명확한 프로필 있으면 바로 사용
    - 없으면 보조 키워드(예: "○○ 창업자 인터뷰")로 fallback
3. **Loop 처리**
    - 최대 2개 소스 이상 매칭 → 상호 비교 요약
4. **요약 시 전략**
    - 경력 강조, 부정적 이슈 체크, 스타트업 경력 여부 분리


# 5. 투자 판단 에이전트

### 목적
각 기업 별 투자 가치 평가 및 우선순위 부여

### 사용한 RAG 문서
벤처캐피탈 자율규제 우수기업
1페이지씩 자르기 + 표 추출 + 텍스트 청크 단위 임베딩 진행

### 진행 방향
기업 정보 -> 각 요소별 가중치(weight) 부여
- Owner (30%): 창업자/팀 역량
- Opportunity (25%): 시장 기회 크기
- Product (15%): 제품/기술 우수성
- Competitive (10%): 경쟁우위
- Performance (10%): 실적/성장성
- Deal Terms (10%): 투자조건
2. RAG 기반 적/부 판단
3. 종합하여 우선순위 순위 조정

---

# 보고서 생성 에이전트 심화

- 스타트업별 기본정보, 기술력, 시장성, 경쟁력, 창업자 평가 종합
- 표와 자연어 설명을 결합한 **읽기 좋은 투자 보고서** 자동 생성
- 일관된 포맷 + 부드러운 서술 흐름 유지

- 투자 보고서 생성 에이전트
- 문서 처리 파이프라인
- 분석 결과 로드 → 분석 결과 통합 → ReportLab PDF 생성

### 핵심 컴포넌트
문서 생성 도구: ReportLab
임베딩 모델: 없음 (기존 분석 결과 활용)
벡터 저장소: 없음
언어 모델: GPT-4
검색 시스템: 없음
문서별 처리 방법
ParagraphStyle로 한글 처리

### 처리 단계
1. 분석 결과 통합
   - 시장, 기술, 경쟁사, 창업자 분석 결과 수집
   - 각 데이터 필드 유효성 검증 및 표준화
2. 요약 및 추천사항 생성
   - 핵심 요약 텍스트 생성
   - 투자 이유 및 위험 요소 추출
   - 종합 추천 메시지 작성
3. PDF 보고서 생성
   - ReportLab을 사용한 전문적 PDF 포맷팅
   - 테이블, 색상 테마, 구조화된 섹션 포함
   - 한글 폰트 적용을 통한 가독성 확보



---

