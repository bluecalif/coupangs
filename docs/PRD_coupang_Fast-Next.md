# 쿠팡 카피캣 PRD - 전자상거래 데이터 분석 대시보드

## 🎯 프로젝트 개요

### 제품명
**CoupangCopyCat** - 전자상거래 시장 분석 대시보드

### 제품 비전
판매자들이 쿠팡 마켓플레이스에서 상품 판매 전략을 수립할 수 있도록 시장 데이터를 종합 분석하여 제공하는 대시보드

### 핵심 가치 제안
- 실시간 상품 시장 분석
- 경쟁사 가격 및 판매량 분석
- 광고 비용 최적화 인사이트
- 트렌드 기반 상품 발굴

---

## 📋 기능 요구사항

### 1. 데이터 수집 엔진 (백엔드)

#### 1.1 쿠팡 메인 마켓플레이스 분석
**엔드포인트**: `/api/coupang/search`
```json
{
  "keyword": "무선이어폰",
  "page": 1,
  "sort": "scoreDesc"
}
```

**수집 데이터**:
- 상품명, 상품코드, 가격
- 리뷰 수, 평점
- 판매자 정보
- 배송 형태 (로켓배송 여부)
- 썸네일 이미지 URL

**기술 구현**:
- Selenium + undetected-chromedriver
- 페이지네이션 처리
- Rate limiting (1초당 1요청)
- 캐싱 (Redis, 1시간)

#### 1.2 쿠팡 윙스 카탈로그 분석  
**엔드포인트**: `/api/coupang-wings/catalog`
```json
{
  "product_code": "1234567890",
  "auth_token": "encrypted_session"
}
```

**수집 데이터**:
- 카탈로그 조회수
- 경쟁 상품 수
- 예상 월 판매량

#### 1.3 쿠팡 광고센터 키워드 분석
**엔드포인트**: `/api/coupang-ads/keywords`
```json
{
  "keywords": ["무선이어폰", "블루투스이어폰"],
  "auth_token": "encrypted_session"
}
```

**수집 데이터**:
- 키워드별 광고 단가
- 경쟁 강도
- 예상 클릭률

#### 1.4 네이버 데이터랩 트렌드 분석
**엔드포인트**: `/api/naver/trends`
```json
{
  "keyword": "무선이어폰",
  "period": "5y"
}
```

**수집 데이터**:
- 월별/주별 검색량 트렌드
- 연관 검색어
- 성별/연령대별 관심도

### 2. 데이터 처리 및 분석

#### 2.1 리뷰 텍스트 분석
- **감정 분석**: 긍정/부정/중립 비율
- **키워드 추출**: 자주 언급되는 특징
- **만족도 점수**: 종합 만족도 계산

#### 2.2 판매량 추정 알고리즘
```python
def estimate_sales(review_count, days_since_launch, category_factor):
    base_conversion = 0.02  # 2% 구매 전환율
    estimated_monthly_sales = (review_count / base_conversion) / (days_since_launch / 30)
    return estimated_monthly_sales * category_factor
```

---

## 🎨 프론트엔드 설계

### 3. 대시보드 UI/UX

#### 3.1 메인 대시보드 레이아웃
**Grid System**: 4행 × 2열 = 8개 위젯

```
┌─────────────────────┬─────────────────────┐
│   1. 가격 분포       │   2. 리뷰수 분포     │
├─────────────────────┼─────────────────────┤
│   3. 판매량 트렌드   │   4. 조회수 분석     │
├─────────────────────┼─────────────────────┤
│   5. 판매형태 분석   │   6. 광고단가 분석   │
├─────────────────────┼─────────────────────┤
│   7. 검색 트렌드     │   8. 리뷰 분석       │
└─────────────────────┴─────────────────────┘
```

#### 3.2 각 위젯별 상세 스펙

**1. 가격 분포 (Bar Chart)**
- X축: 상품명 (상위 20개)
- Y축: 가격 (원)
- 정렬: 가격 오름차순
- 색상: 가격대별 gradient

**2. 리뷰수 분포 (Bar Chart)**
- X축: 상품명 (상위 20개)
- Y축: 리뷰 수
- 정렬: 리뷰수 오름차순
- 툴팁: 평점 정보 포함

**3. 판매량 트렌드 (Line Chart)**
- X축: 날짜 (최근 30일)
- Y축: 추정 일 판매량
- 라인: 상위 10개 상품
- 인터랙션: 상품별 on/off

**4. 조회수 분석 (Horizontal Bar Chart)**
- X축: 조회수
- Y축: 상품명
- 정렬: 조회수 오름차순
- 배경: 카테고리별 색상 구분

**5. 판매형태 분석 (Donut Chart)**
- 세그먼트: 로켓배송, 일반배송, 해외배송
- 레이블: 비율 및 개수
- 색상: 브랜드 컬러 적용

**6. 광고단가 분석 (Horizontal Bar Chart)**
- X축: 키워드별 CPC (원)
- Y축: 키워드명
- 정렬: CPC 높은 순
- 추가 정보: 경쟁 강도 표시

**7. 검색 트렌드 (Area Chart)**
- X축: 월별 (최근 3년)
- Y축: 검색량 지수
- 영역: 검색량 변화
- 이벤트 마커: 특이점 표시

**8. 리뷰 분석 (Word Cloud + Pie Chart)**
- 워드클라우드: 주요 키워드
- 파이차트: 감정 분석 결과
- 만족도 스코어: 게이지 차트

#### 3.3 반응형 디자인
- **Desktop**: 4×2 Grid
- **Tablet**: 2×4 Grid  
- **Mobile**: 1×8 Stack

---

## 🛠 기술 스택

### 4. 백엔드 (FastAPI)

#### 4.1 프로젝트 구조
```
backend/
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── product.py
│   │   ├── review.py
│   │   └── trend.py
│   ├── services/
│   │   ├── scraper/
│   │   │   ├── coupang_scraper.py
│   │   │   ├── wings_scraper.py
│   │   │   ├── ads_scraper.py
│   │   │   └── naver_scraper.py
│   │   ├── analyzer/
│   │   │   ├── price_analyzer.py
│   │   │   ├── review_analyzer.py
│   │   │   └── trend_analyzer.py
│   │   └── cache/
│   │       └── redis_client.py
│   ├── api/
│   │   ├── search.py
│   │   ├── analysis.py
│   │   └── trends.py
│   └── utils/
│       ├── data_validator.py
│       └── rate_limiter.py
├── requirements.txt
└── Dockerfile
```

#### 4.2 핵심 의존성
```txt
fastapi==0.104.1
uvicorn==0.24.0
selenium==4.15.0
undetected-chromedriver==3.5.4
beautifulsoup4==4.12.2
requests==2.31.0
redis==5.0.1
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
```

### 5. 프론트엔드 (Next.js)

#### 5.1 프로젝트 구조
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   └── api/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── PriceChart.tsx
│   │   │   ├── ReviewChart.tsx
│   │   │   ├── SalesChart.tsx
│   │   │   ├── ViewChart.tsx
│   │   │   ├── SalesTypeChart.tsx
│   │   │   ├── AdCostChart.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   └── ReviewAnalysis.tsx
│   │   ├── ui/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   └── styles/
│       └── globals.css
├── package.json
└── next.config.js
```

#### 5.2 핵심 의존성
```json
{
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "recharts": "2.8.0",
    "tailwindcss": "3.3.0",
    "axios": "1.5.0",
    "react-query": "3.39.0",
    "framer-motion": "10.16.0",
    "lucide-react": "0.290.0"
  }
}
```

### 6. 차트 라이브러리 (Recharts)

#### 6.1 차트별 컴포넌트 매핑
```typescript
// 가격 분포 - Bar Chart
<BarChart data={priceData}>
  <XAxis dataKey="productName" />
  <YAxis />
  <Bar dataKey="price" fill="#8884d8" />
</BarChart>

// 판매량 트렌드 - Line Chart  
<LineChart data={salesData}>
  <XAxis dataKey="date" />
  <YAxis />
  <Line type="monotone" dataKey="sales" stroke="#8884d8" />
</LineChart>

// 판매형태 - Pie Chart
<PieChart>
  <Pie data={salesTypeData} dataKey="value" />
</PieChart>
```

---

## 🚀 배포 및 운영

### 7. 인프라 구성

#### 7.1 Vercel 배포 설정
```json
// vercel.json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

#### 7.2 환경 변수 관리
```env
# Backend
REDIS_URL=redis://localhost:6379
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
COUPANG_SESSION_KEY=encrypted_session

# Frontend  
NEXT_PUBLIC_API_BASE_URL=https://your-domain.vercel.app/api
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## ⚠️ 중요 고려사항

### 8. 법적/윤리적 주의사항

#### 8.1 웹 스크래핑 준수사항
- **robots.txt 확인**: 각 사이트의 크롤링 정책 준수
- **Rate Limiting**: 서버 부하 방지를 위한 요청 제한
- **User-Agent 설정**: 봇임을 명시하고 연락처 포함
- **이용약관 검토**: 각 플랫폼의 ToS 위반 방지

#### 8.2 데이터 사용 제한
- **상업적 사용 금지**: 개인 학습/연구 목적으로만 사용
- **데이터 재배포 금지**: 수집된 데이터의 제3자 제공 금지
- **개인정보 보호**: 판매자/구매자 개인정보 수집 금지

#### 8.3 기술적 대응 방안
- **CAPTCHA 우회 금지**: 자동화 탐지 시 중단
- **로그인 자동화 제한**: 수동 인증 후 세션 사용
- **백업 데이터 소스**: API 제공 서비스 우선 활용

---

## 📊 개발 일정

### 9. 마일스톤

#### Phase 1: MVP (2주)
- [x] FastAPI 기본 구조 설정
- [x] 쿠팡 기본 검색 스크래퍼 구현
- [x] Next.js 대시보드 기본 레이아웃
- [x] 가격/리뷰수 차트 구현

#### Phase 2: 기능 확장 (3주)
- [ ] 쿠팡윙스/광고센터 스크래퍼 추가
- [ ] 네이버 데이터랩 연동
- [ ] 고급 차트 (트렌드, 분석) 구현
- [ ] 리뷰 텍스트 분석 기능

#### Phase 3: 배포 및 최적화 (1주)
- [ ] Vercel 배포 설정
- [ ] 성능 최적화
- [ ] 에러 핸들링 개선
- [ ] 사용자 테스트 및 피드백

---

## 🔗 API 문서

### 10. 주요 엔드포인트

```typescript
// 상품 검색
GET /api/search?keyword={keyword}&page={page}
Response: {
  products: Product[],
  totalCount: number,
  hasNext: boolean
}

// 대시보드 데이터
GET /api/dashboard?keyword={keyword}
Response: {
  priceData: PriceData[],
  reviewData: ReviewData[], 
  salesData: SalesData[],
  trendData: TrendData[],
  analysisData: AnalysisData
}

// 트렌드 분석
GET /api/trends?keyword={keyword}&period={period}
Response: {
  trendPoints: TrendPoint[],
  relatedKeywords: string[],
  insights: string[]
}
```

