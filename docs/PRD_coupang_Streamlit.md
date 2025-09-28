# 쿠팡 카피캣 PRD - Streamlit 버전

## 🎯 프로젝트 개요

### 제품명
**CoupangCopyCat Analytics** - Streamlit 기반 데이터 분석 웹앱

### 제품 비전
**가장 빠르고 간단한** 쿠팡 시장 분석 도구 - Python 한 언어로 완성하는 All-in-One 솔루션

### 핵심 가치 제안
- **Ultra 빠른 개발**: 하루만에 MVP 완성 가능
- **Python Only**: 프론트엔드 지식 불필요
- **즉시 배포**: Streamlit Cloud로 원클릭 배포
- **데이터 사이언스 친화적**: Pandas, Plotly 등 익숙한 도구 활용

---

## 🏗 아키텍처 설계

### 전체 구조 (Single Python Application)
```
┌─────────────────────────────────────┐
│         Streamlit Web App           │
├─────────────────────────────────────┤
│  📁 File Upload (st.file_uploader)  │
│  🔍 HTML Parsing (BeautifulSoup)    │
│  📊 Data Analysis (Pandas/NumPy)    │
│  📈 Visualization (Plotly/Altair)   │
│  💾 Session State Management        │
├─────────────────────────────────────┤
│        Streamlit Cloud 배포         │
│     (GitHub 연동 자동 배포)         │
└─────────────────────────────────────┘
```

### 기술 스택 (Python Ecosystem)
- **웹 프레임워크**: Streamlit
- **HTML 파싱**: BeautifulSoup4, lxml
- **데이터 처리**: Pandas, NumPy
- **차트**: Plotly, Altair, Matplotlib
- **텍스트 분석**: NLTK, KoNLPy (한국어)
- **파일 처리**: io, base64
- **배포**: Streamlit Cloud (무료)

---

## 📋 기능 요구사항

### 1. Streamlit 앱 기본 구조

#### 1.1 메인 인터페이스
```python
# main.py
import streamlit as st
import pandas as pd
import plotly.express as px
from parsers.coupang_parser import CoupangParser
from analyzers.price_analyzer import PriceAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="쿠팡 카피캣 - 시장 분석",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 타이틀
st.title("🛒 쿠팡 카피캣 - 시장 분석 도구")
st.markdown("HTML 파일을 업로드하여 즉시 시장 데이터를 분석하세요!")

# 사이드바 - 파일 업로드
with st.sidebar:
    st.header("📁 파일 업로드")
    
    search_html = st.file_uploader(
        "쿠팡 검색 결과 HTML (필수)",
        type=['html', 'htm'],
        key="search_html"
    )
    
    product_html = st.file_uploader(
        "상품 상세 페이지 HTML (필수)",
        type=['html', 'htm'], 
        key="product_html"
    )
    
    wings_html = st.file_uploader(
        "쿠팡윙스 HTML (선택)",
        type=['html', 'htm'],
        key="wings_html"
    )
    
    ads_html = st.file_uploader(
        "광고센터 HTML (선택)",
        type=['html', 'htm'],
        key="ads_html"
    )
    
    trends_html = st.file_uploader(
        "네이버 트렌드 HTML (선택)",
        type=['html', 'htm'],
        key="trends_html"
    )

# 분석 시작 버튼
if search_html and product_html:
    if st.button("🚀 분석 시작", type="primary"):
        analyze_data(search_html, product_html, wings_html, ads_html, trends_html)
else:
    st.info("🔺 필수 파일(검색 결과 + 상품 상세)을 업로드해주세요")
```

#### 1.2 파일 업로드 및 읽기
```python
@st.cache_data
def read_html_file(uploaded_file):
    """업로드된 HTML 파일을 읽어 문자열로 반환"""
    if uploaded_file is not None:
        return uploaded_file.read().decode('utf-8')
    return None

@st.cache_data
def parse_coupang_search(html_content):
    """쿠팡 검색 결과 HTML 파싱"""
    parser = CoupangParser()
    return parser.parse_search_html(html_content)

@st.cache_data
def parse_product_detail(html_content):
    """상품 상세 페이지 HTML 파싱"""
    parser = ProductDetailParser()
    return parser.parse_product_detail(html_content)
```

### 2. HTML 파싱 엔진 (Python)

#### 2.1 쿠팡 검색 결과 파싱
```python
# parsers/coupang_parser.py
from bs4 import BeautifulSoup
import pandas as pd
import re

class CoupangParser:
    def parse_search_html(self, html_content):
        """쿠팡 검색 결과 HTML에서 상품 정보 추출"""
        soup = BeautifulSoup(html_content, 'lxml')
        products = []
        
        # 상품 목록 파싱
        product_items = soup.find_all('li', {'data-product-id': True})
        
        for item in product_items:
            try:
                product = {
                    'product_id': item.get('data-product-id'),
                    'name': self._extract_name(item),
                    'price': self._extract_price(item),
                    'original_price': self._extract_original_price(item),
                    'discount_rate': self._extract_discount_rate(item),
                    'review_count': self._extract_review_count(item),
                    'rating': self._extract_rating(item),
                    'is_rocket': self._is_rocket_delivery(item),
                    'is_fresh': self._is_fresh_product(item),
                    'seller': self._extract_seller(item),
                    'image_url': self._extract_image_url(item),
                    'product_url': self._extract_product_url(item)
                }
                products.append(product)
            except Exception as e:
                st.warning(f"상품 파싱 중 오류: {e}")
                continue
        
        return pd.DataFrame(products)
    
    def _extract_price(self, item):
        """가격 추출"""
        price_elem = item.find('strong', class_='price-value')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            return int(re.sub(r'[^\d]', '', price_text))
        return 0
    
    def _extract_review_count(self, item):
        """리뷰 수 추출"""
        review_elem = item.find('span', class_='rating-total-count')
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            return int(re.sub(r'[^\d]', '', review_text))
        return 0
    
    def _extract_rating(self, item):
        """평점 추출"""
        rating_elem = item.find('em', class_='rating')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            return float(rating_text) if rating_text else 0
        return 0
    
    def _is_rocket_delivery(self, item):
        """로켓배송 여부"""
        return bool(item.find('span', class_='rocket'))
    
    def _extract_seller(self, item):
        """판매자 정보 추출"""
        seller_elem = item.find('span', class_='seller-name')
        return seller_elem.get_text(strip=True) if seller_elem else "쿠팡"
```

#### 2.2 상품 상세 페이지 파싱
```python
# parsers/product_detail_parser.py
class ProductDetailParser:
    def parse_product_detail(self, html_content):
        """상품 상세 페이지에서 리뷰, 스펙 등 추출"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        return {
            'reviews': self._extract_reviews(soup),
            'specifications': self._extract_specifications(soup),
            'images': self._extract_images(soup),
            'sales_info': self._extract_sales_info(soup),
            'qna': self._extract_qna(soup)
        }
    
    def _extract_reviews(self, soup):
        """리뷰 데이터 추출"""
        reviews = []
        review_items = soup.find_all('article', class_='sdp-review__article__list')
        
        for item in review_items:
            try:
                review = {
                    'rating': self._extract_review_rating(item),
                    'content': self._extract_review_content(item),
                    'date': self._extract_review_date(item),
                    'helpful_count': self._extract_helpful_count(item),
                    'verified_purchase': self._is_verified_purchase(item),
                    'product_info': self._extract_product_info(item)
                }
                reviews.append(review)
            except Exception as e:
                continue
        
        return pd.DataFrame(reviews)
    
    def _extract_review_rating(self, item):
        """리뷰 평점 추출"""
        rating_elem = item.find('div', class_='sdp-review__article__list__info__product-info__star-orange')
        if rating_elem:
            style = rating_elem.get('style', '')
            width_match = re.search(r'width:\s*(\d+(?:\.\d+)?)%', style)
            if width_match:
                return round(float(width_match.group(1)) / 20, 1)  # 100% = 5점
        return 0
```

### 3. 데이터 분석 엔진

#### 3.1 가격 분석
```python
# analyzers/price_analyzer.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class PriceAnalyzer:
    def __init__(self, products_df):
        self.products_df = products_df
    
    def analyze_prices(self):
        """가격 데이터 종합 분석"""
        prices = self.products_df['price'].dropna()
        prices = prices[prices > 0]
        
        analysis = {
            'basic_stats': self._calculate_basic_stats(prices),
            'price_distribution': self._analyze_price_distribution(prices),
            'rocket_vs_normal': self._compare_rocket_prices(),
            'seller_analysis': self._analyze_by_seller(),
            'discount_analysis': self._analyze_discounts()
        }
        
        return analysis
    
    def _calculate_basic_stats(self, prices):
        """기본 통계 계산"""
        return {
            'count': len(prices),
            'mean': prices.mean(),
            'median': prices.median(),
            'std': prices.std(),
            'min': prices.min(),
            'max': prices.max(),
            'q25': prices.quantile(0.25),
            'q75': prices.quantile(0.75)
        }
    
    def _analyze_price_distribution(self, prices):
        """가격 분포 분석"""
        # 가격 구간별 분포
        bins = [0, 10000, 30000, 50000, 100000, 200000, float('inf')]
        labels = ['1만원 미만', '1-3만원', '3-5만원', '5-10만원', '10-20만원', '20만원 이상']
        
        price_ranges = pd.cut(prices, bins=bins, labels=labels, include_lowest=True)
        distribution = price_ranges.value_counts().sort_index()
        
        return distribution
    
    def create_price_chart(self):
        """가격 분포 차트 생성"""
        analysis = self.analyze_prices()
        distribution = analysis['price_distribution']
        
        fig = px.bar(
            x=distribution.index,
            y=distribution.values,
            title="💰 가격 구간별 상품 분포",
            labels={'x': '가격 구간', 'y': '상품 수'},
            color=distribution.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
```

#### 3.2 리뷰 분석 (감정 분석 포함)
```python
# analyzers/review_analyzer.py
import re
from collections import Counter
from konlpy.tag import Okt  # 한국어 형태소 분석

class ReviewAnalyzer:
    def __init__(self, reviews_df):
        self.reviews_df = reviews_df
        self.okt = Okt()
    
    def analyze_reviews(self):
        """리뷰 종합 분석"""
        return {
            'basic_stats': self._calculate_review_stats(),
            'sentiment_analysis': self._analyze_sentiment(),
            'keyword_analysis': self._extract_keywords(),
            'rating_distribution': self._analyze_rating_distribution(),
            'temporal_analysis': self._analyze_review_trends()
        }
    
    def _analyze_sentiment(self):
        """감정 분석"""
        positive_words = ['좋', '만족', '추천', '훌륭', '완벽', '빠름', '깔끔', '품질']
        negative_words = ['나쁨', '불만', '안좋', '느림', '문제', '별로', '실망', '불량']
        
        sentiments = []
        
        for content in self.reviews_df['content'].dropna():
            content_lower = content.lower()
            positive_score = sum(1 for word in positive_words if word in content_lower)
            negative_score = sum(1 for word in negative_words if word in content_lower)
            
            if positive_score > negative_score:
                sentiments.append('긍정')
            elif negative_score > positive_score:
                sentiments.append('부정')
            else:
                sentiments.append('중립')
        
        sentiment_counts = Counter(sentiments)
        total = len(sentiments)
        
        return {
            'positive_ratio': sentiment_counts['긍정'] / total * 100,
            'negative_ratio': sentiment_counts['부정'] / total * 100,
            'neutral_ratio': sentiment_counts['중립'] / total * 100,
            'total_reviews': total
        }
    
    def _extract_keywords(self):
        """핵심 키워드 추출"""
        all_text = ' '.join(self.reviews_df['content'].dropna())
        
        # 형태소 분석 및 명사 추출
        nouns = self.okt.nouns(all_text)
        
        # 불용어 제거 및 길이 제한
        stopwords = ['상품', '제품', '구매', '주문', '배송', '쿠팡', '포장']
        filtered_nouns = [noun for noun in nouns 
                         if len(noun) > 1 and noun not in stopwords]
        
        # 빈도수 계산
        keyword_counts = Counter(filtered_nouns)
        top_keywords = keyword_counts.most_common(20)
        
        return top_keywords
    
    def create_sentiment_chart(self):
        """감정 분석 결과 차트"""
        sentiment_data = self._analyze_sentiment()
        
        labels = ['긍정', '중립', '부정']
        values = [
            sentiment_data['positive_ratio'],
            sentiment_data['neutral_ratio'],
            sentiment_data['negative_ratio']
        ]
        colors = ['#28a745', '#ffc107', '#dc3545']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values,
            hole=0.4,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title="😊 리뷰 감정 분석",
            height=400
        )
        
        return fig
```

### 4. Streamlit 대시보드 구성

#### 4.1 메인 분석 함수
```python
def analyze_data(search_html, product_html, wings_html, ads_html, trends_html):
    """메인 분석 실행 함수"""
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1단계: HTML 파싱
        status_text.text('📄 HTML 파일 파싱 중...')
        progress_bar.progress(20)
        
        search_content = read_html_file(search_html)
        product_content = read_html_file(product_html)
        
        # 2단계: 데이터 추출
        status_text.text('🔍 상품 데이터 추출 중...')
        progress_bar.progress(40)
        
        products_df = parse_coupang_search(search_content)
        product_details = parse_product_detail(product_content)
        
        # 3단계: 데이터 분석
        status_text.text('📊 데이터 분석 중...')
        progress_bar.progress(60)
        
        price_analyzer = PriceAnalyzer(products_df)
        review_analyzer = ReviewAnalyzer(product_details['reviews'])
        
        # 4단계: 결과 시각화
        status_text.text('📈 결과 시각화 중...')
        progress_bar.progress(80)
        
        display_analysis_results(products_df, price_analyzer, review_analyzer)
        
        progress_bar.progress(100)
        status_text.text('✅ 분석 완료!')
        
        # 세션 상태에 결과 저장
        st.session_state['analysis_complete'] = True
        st.session_state['products_df'] = products_df
        
    except Exception as e:
        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
        st.stop()

def display_analysis_results(products_df, price_analyzer, review_analyzer):
    """분석 결과 대시보드 표시"""
    
    st.success("🎉 분석이 완료되었습니다!")
    
    # 요약 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 상품 수", len(products_df))
    
    with col2:
        avg_price = products_df['price'].mean()
        st.metric("평균 가격", f"₩{avg_price:,.0f}")
    
    with col3:
        total_reviews = products_df['review_count'].sum()
        st.metric("총 리뷰 수", f"{total_reviews:,}")
    
    with col4:
        rocket_ratio = (products_df['is_rocket'].sum() / len(products_df)) * 100
        st.metric("로켓배송 비율", f"{rocket_ratio:.1f}%")
    
    # 탭으로 구분된 상세 분석
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 가격 분석", "⭐ 리뷰 분석", "🚀 판매 형태", "📈 트렌드", "📋 상품 목록"
    ])
    
    with tab1:
        display_price_analysis(price_analyzer)
    
    with tab2:
        display_review_analysis(review_analyzer)
    
    with tab3:
        display_sales_analysis(products_df)
    
    with tab4:
        display_trend_analysis()
    
    with tab5:
        display_product_list(products_df)
```

#### 4.2 개별 분석 페이지
```python
def display_price_analysis(price_analyzer):
    """가격 분석 탭"""
    st.subheader("💰 가격 분포 분석")
    
    # 가격 분포 차트
    price_chart = price_analyzer.create_price_chart()
    st.plotly_chart(price_chart, use_container_width=True)
    
    # 통계 요약
    analysis = price_analyzer.analyze_prices()
    stats = analysis['basic_stats']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 기본 통계")
        st.write(f"• **평균 가격**: ₩{stats['mean']:,.0f}")
        st.write(f"• **중간값**: ₩{stats['median']:,.0f}")
        st.write(f"• **최저가**: ₩{stats['min']:,.0f}")
        st.write(f"• **최고가**: ₩{stats['max']:,.0f}")
    
    with col2:
        st.markdown("### 🎯 가격 구간별 분포")
        distribution = analysis['price_distribution']
        for range_name, count in distribution.items():
            percentage = (count / distribution.sum()) * 100
            st.write(f"• **{range_name}**: {count}개 ({percentage:.1f}%)")

def display_review_analysis(review_analyzer):
    """리뷰 분석 탭"""
    st.subheader("⭐ 리뷰 감정 분석")
    
    # 감정 분석 차트
    sentiment_chart = review_analyzer.create_sentiment_chart()
    st.plotly_chart(sentiment_chart, use_container_width=True)
    
    # 키워드 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔑 핵심 키워드")
        keywords = review_analyzer._extract_keywords()
        keyword_df = pd.DataFrame(keywords, columns=['키워드', '빈도'])
        st.dataframe(keyword_df.head(10), use_container_width=True)
    
    with col2:
        st.markdown("### 📈 평점 분포")
        # 평점 히스토그램 생성
        reviews_df = review_analyzer.reviews_df
        if not reviews_df.empty:
            fig = px.histogram(
                reviews_df, 
                x='rating', 
                nbins=10,
                title="평점 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
```

### 5. 사용자 가이드 및 도움말

#### 5.1 사이드바 가이드
```python
def display_user_guide():
    """사용자 가이드 표시"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📖 사용 가이드")
        
        with st.expander("🔍 HTML 파일 저장 방법"):
            st.markdown("""
            **쿠팡 검색 결과 HTML:**
            1. 쿠팡에서 원하는 키워드 검색
            2. 검색 결과 페이지에서 `Ctrl+S`
            3. '웹페이지, 완료' 형식으로 저장
            
            **상품 상세 페이지 HTML:**
            1. 분석하고 싶은 상품 클릭
            2. 상품 상세 페이지에서 `Ctrl+S`
            3. '웹페이지, 완료' 형식으로 저장
            """)
        
        with st.expander("⚠️ 주의사항"):
            st.markdown("""
            • HTML 파일은 최대 200MB까지 지원
            • 개인정보가 포함된 페이지는 업로드 금지
            • 분석된 데이터는 서버에 저장되지 않음
            • 상업적 사용 시 각 사이트 이용약관 확인 필요
            """)
        
        with st.expander("💡 분석 팁"):
            st.markdown("""
            • 동일한 검색어로 여러 페이지 분석 시 더 정확한 결과
            • 베스트셀러 상품의 상세 페이지 선택 권장
            • 시간대별 비교를 위해 파일명에 날짜 포함
            """)
```

---

## 🚀 배포 및 실행

### 6. 로컬 실행

#### 6.1 프로젝트 구조
```
coupang-copycat-streamlit/
├── main.py                    # 메인 Streamlit 앱
├── requirements.txt           # 의존성 패키지
├── README.md                 # 프로젝트 설명
├── .streamlit/
│   └── config.toml           # Streamlit 설정
├── parsers/
│   ├── __init__.py
│   ├── coupang_parser.py     # 쿠팡 HTML 파싱
│   ├── product_detail_parser.py
│   ├── wings_parser.py       # 쿠팡윙스 파싱
│   └── naver_parser.py       # 네이버 트렌드 파싱
├── analyzers/
│   ├── __init__.py
│   ├── price_analyzer.py     # 가격 분석
│   ├── review_analyzer.py    # 리뷰/감정 분석
│   └── trend_analyzer.py     # 트렌드 분석
├── utils/
│   ├── __init__.py
│   ├── data_validator.py     # 데이터 검증
│   └── chart_helpers.py      # 차트 유틸리티
└── assets/
    ├── sample_search.html     # 샘플 HTML 파일
    └── user_guide.md         # 사용자 가이드
```

#### 6.2 의존성 패키지
```txt
# requirements.txt
streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
beautifulsoup4==4.12.2
lxml==4.9.3
plotly==5.15.0
altair==5.0.0
konlpy==0.6.0
wordcloud==1.9.2
python-dateutil==2.8.2
requests==2.31.0
```

#### 6.3 실행 방법
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run main.py

# 브라우저에서 자동으로 http://localhost:8501 열림
```

### 7. Streamlit Cloud 배포

#### 7.1 GitHub 연동 배포
```bash
# 1. GitHub 리포지토리 생성
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/coupang-copycat.git
git push -u origin main

# 2. Streamlit Cloud에서 배포
# - https://share.streamlit.io 접속
# - GitHub 연동
# - 리포지토리 선택
# - main.py 지정
# - Deploy 클릭
```

#### 7.2 Streamlit 설정 파일
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false
```

---

## 📊 개발 일정

### 8. 마일스톤 (Streamlit 버전)

#### Phase 1: 기본 구조 (1-2일) 🚀
- [x] Streamlit 앱 기본 구조
- [x] 파일 업로드 인터페이스
- [x] HTML 파일 읽기 및 기본 파싱
- [x] 샘플 차트 표시

#### Phase 2: 파싱 엔진 (2-3일)
- [ ] 쿠팡 검색 결과 파싱 완성
- [ ] 상품 상세 페이지 파싱
- [ ] 데이터 검증 및 오류 처리
- [ ] 캐싱으로 성능 최적화

#### Phase 3: 분석 엔진 (2-3일)
- [ ] 가격 분석 모듈 완성
- [ ] 리뷰 감정 분석 (한국어 지원)
- [ ] 키워드 추출 및 워드클라우드
- [ ] 판매 형태 분석

#### Phase 4: 시각화 및 UX (1-2일)
- [ ] Plotly 차트 완성
- [ ] 반응형 대시보드 레이아웃
- [ ] 사용자 가이드 및 도움말
- [ ] 데이터 내보내기 기능

#### Phase 5: 배포 및 완성 (1일)
- [ ] Streamlit Cloud 배포
- [ ] 성능 테스트 및 최적화
- [ ] 문서화 완성
- [ ] 사용자 테스트

**총 개발 기간**: **7-11일** (약 1.5-2주)

---

## 🎯 핵심 장점

### Streamlit 방식의 혁신성

**🚀 개발 속도 최강**
- **하루 만에 MVP**: 가장 빠른 프로토타이핑
- **Python Only**: 프론트엔드 지식 완전 불필요
- **코드 20% 감소**: FastAPI+Next.js 대비 현저히 적은 코드량

**🐍 Python 생태계 활용**
- **데이터 사이언스 도구**: Pandas, NumPy, Scikit-learn 자유 활용
- **시각화 라이브러리**: Plotly, Matplotlib, Seaborn 모두 지원
- **한국어 처리**: KoNLPy로 완벽한 한국어 자연어 처리

**🎨 내장 UI 컴포넌트**
```python
# 복잡한 HTML/CSS 없이 바로 사용 가능
st.file_uploader()     # 파일 업로드
st.selectbox()         # 드롭다운
st.slider()            # 슬라이더
st.dataframe()         # 데이터 테이블
st.plotly_chart()      # 차트
st.columns()           # 레이아웃
```

**💰 완전 무료 배포**
- **Streamlit Cloud**: GitHub 연동으로 무료 배포
- **자동 배포**: 코드 푸시 시 자동 업데이트
- **HTTPS 기본**: SSL 인증서 자동 적용

**🔧 즉시 실행**
```bash
streamlit run main.py  # 한 줄로 실행 완료
```

---

## 📋 세 가지 방식 최종 비교

| 구분 | FastAPI + Next.js | Next.js Only | **Streamlit** |
|------|-------------------|---------------|---------------|
| **개발 기간** | 4-6주 | 2-3주 | **1.5-2주** ⭐ |
| **코드 복잡도** | 높음 | 중간 | **낮음** ⭐ |
| **실행 방법** | 2개 서버 | npm run dev | **streamlit run** ⭐ |
| **Python 활용** | 제한적 | 불가 | **완전 활용** ⭐ |
| **데이터 분석** | 어려움 | 어려움 | **매우 쉬움** ⭐ |
| **배포 복잡도** | 높음 | 낮음 | **매우 낮음** ⭐ |
| **운영 비용** | 서버 비용 | 무료 | **무료** ⭐ |
| **확장성** | 높음 | 중간 | 중간 |
| **UI 커스터마이징** | 높음 | 높음 | 제한적 |

## 🎯 최종 권장사항

### **MVP에는 Streamlit을 강력 추천합니다!** ⭐

**이유**:
1. **가장 빠른 개발**: 1.5-2주면 완성
2. **Python 생태계**: 데이터 분석에 최적화
3. **학습 곡선**: 가장 낮은 진입 장벽
4. **즉시 검증**: 빠른 아이디어 검증 가능

**Streamlit이 적합한 경우**:
- MVP나 프로토타입 개발
- 데이터 분석 중심 도구
- Python 개발자
- 빠른 시장 검증 필요

**다른 방식이 적합한 경우**:
- 커스텀 UI가 중요한 B2C 서비스
- 대규모 트래픽 처리 필요
- 복잡한 사용자 인터랙션 필요

어떤 방식으로 시작하시겠어요? Streamlit로 하시면 **오늘 당장** 시작해서 **일주일 안에** 결과를 볼 수 있습니다! 🚀