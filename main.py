import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from parsers.coupang_parser import CoupangParser
from parsers.product_detail_parser import ProductDetailParser
from analyzers.price_analyzer import PriceAnalyzer  # PriceAnalyzer 임포트
from analyzers.review_analyzer import ReviewAnalyzer  # ReviewAnalyzer 임포트
from analyzers.delivery_analyzer import DeliveryAnalyzer  # DeliveryAnalyzer 임포트
import logging

# --- 로깅 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="debug.log",
    filemode="w",  # 'w'는 실행할 때마다 파일을 새로 씀
    encoding="utf-8",  # 한글 인코딩 문제 해결
)
# -----------------

# from analyzers.price_analyzer import PriceAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="쿠팡 카피캣 - 시장 분석",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 메인 타이틀
st.title("🛒 쿠팡 카피캣 - 시장 분석 도구")

# 캐시 클리어 버튼 (디버깅용)
if st.button("🔄 캐시 클리어 (새로운 분석)", type="secondary"):
    st.cache_data.clear()
    st.success("캐시가 클리어되었습니다. 파일을 다시 업로드하세요.")
    st.rerun()
st.markdown("HTML 파일을 업로드하여 즉시 시장 데이터를 분석하세요!")


def read_html_file(uploaded_file):
    """업로드된 HTML 파일을 읽어 문자열로 반환"""
    if uploaded_file is not None:
        # 파일 포인터를 처음으로 되돌립니다.
        uploaded_file.seek(0)
        return uploaded_file.read().decode("utf-8")
    return None


@st.cache_data
def parse_coupang_search(html_content):
    """쿠팡 검색 결과 HTML 파싱 (캐시 적용)"""
    if not html_content:
        return None
    parser = CoupangParser()
    return parser.parse_search_html(html_content)


@st.cache_data
def parse_product_detail(html_content):
    """상품 상세 페이지 HTML 파싱 (캐시 적용)"""
    if not html_content:
        return None
    parser = ProductDetailParser()
    return parser.parse_product_detail(html_content)


# === 4행 2열 그리드용 분석 함수들 ===


def display_price_analysis_grid(price_analyzer):
    """1행 1열: 가격 분석"""
    st.markdown("#### 💰 가격 분석")

    # 새로운 상품별 가격 막대 차트 표시
    price_chart = price_analyzer.create_product_price_bar_chart()
    st.plotly_chart(price_chart, use_container_width=True)


def display_review_count_analysis(review_analyzer):
    """1행 2열: 리뷰수 분석"""
    st.markdown("#### ⭐ 리뷰수 분석")

    # 새로운 상품별 리뷰 수 막대 차트 표시
    review_chart = review_analyzer.create_product_review_bar_chart()
    st.plotly_chart(review_chart, use_container_width=True)


def display_top10_sales_placeholder():
    """2행 1열: 상위10 판매량 (플레이스홀더)"""
    st.markdown("#### 📈 상위10 판매량")
    st.info("🚧 구현 예정: 과거 1달 판매량 트렌드")

    # 샘플 차트
    sample_data = pd.DataFrame(
        {
            "date": pd.date_range("2024-09-01", periods=30),
            "sales": np.random.randint(100, 500, 30),
        }
    )
    fig = px.line(sample_data, x="date", y="sales", title="샘플: 일별 판매량 트렌드")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def display_view_count_analysis():
    """2행 2열: 조회수 분석 (플레이스홀더)"""
    st.markdown("#### 👀 조회수 분석")
    st.info("🚧 구현 예정: 상품별 조회수 분석")

    # 샘플 차트
    sample_products = ["상품A", "상품B", "상품C", "상품D", "상품E"]
    sample_views = [1500, 1200, 980, 750, 600]

    fig = px.bar(
        x=sample_views,
        y=sample_products,
        orientation="h",
        title="샘플: 조회수 상위 5개 상품",
    )
    fig.update_layout(height=300, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


def display_sales_type_analysis(delivery_analyzer):
    """3행 1열: 판매형태 분석"""
    st.markdown("#### 🚀 판매형태 분석")

    # 배송 타입별 정보 박스 (3개 컬럼)
    delivery_order = ["로켓배송", "그로스", "일반배송"]
    colors = {
        "로켓배송": "#E63946",  # 빨강
        "그로스": "#F77F00",  # 주황
        "일반배송": "#6C757D",  # 회색
    }

    cols = st.columns(3)
    for idx, delivery_type in enumerate(delivery_order):
        count = delivery_analyzer.stats["counts"].get(delivery_type, 0)
        percentage = delivery_analyzer.stats["percentages"].get(delivery_type, 0)

        with cols[idx]:
            # 색상 배경과 함께 정보 박스 표시
            st.markdown(
                f"""
                <div style="
                    background-color: {colors[delivery_type]};
                    color: white;
                    padding: 25px 15px;
                    border-radius: 10px;
                    text-align: center;
                    height: 120px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    box-sizing: border-box;
                ">
                    <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: bold; line-height: 1.2;">{delivery_type}</h3>
                    <h2 style="margin: 0; font-size: 36px; font-weight: bold; line-height: 1;">{percentage:.1f}%</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 박스와 그래프 사이 간격 (80px)
    st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)

    # 그래프 위에 그로스와 일반배송 개수 표시
    gross_count = delivery_analyzer.stats["counts"].get("그로스", 0)
    normal_count = delivery_analyzer.stats["counts"].get("일반배송", 0)

    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 5px; font-size: 14px; color: #666;">
            그로스: {gross_count}개 | 일반배송: {normal_count}개
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 스택 막대 그래프 표시
    delivery_chart = delivery_analyzer.create_delivery_pie_chart()
    if delivery_chart:
        st.plotly_chart(delivery_chart, use_container_width=True)
    else:
        st.info("배송 형태 데이터가 없습니다.")


def display_ads_analysis_placeholder():
    """3행 2열: 광고 분석 (플레이스홀더)"""
    st.markdown("#### 💸 광고 분석")
    st.info("🚧 구현 예정: 광고 단가 및 효율 분석")

    # 샘플 차트
    sample_keywords = ["키워드A", "키워드B", "키워드C", "키워드D"]
    sample_costs = [1200, 980, 850, 600]

    fig = px.bar(x=sample_keywords, y=sample_costs, title="샘플: 키워드별 광고 단가")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def display_search_trends_placeholder():
    """4행 1열: 검색 트렌드 (플레이스홀더)"""
    st.markdown("#### 🔍 검색 트렌드")
    st.info("🚧 구현 예정: 과거 3년 검색 트렌드")

    # 샘플 차트
    sample_data = pd.DataFrame(
        {
            "month": pd.date_range("2022-01", periods=36, freq="M"),
            "search_volume": np.random.randint(50, 100, 36),
        }
    )
    fig = px.line(
        sample_data, x="month", y="search_volume", title="샘플: 월별 검색량 추이"
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def display_review_analysis_placeholder():
    """4행 2열: 리뷰 분석 (플레이스홀더)"""
    st.markdown("#### 📝 리뷰 분석")
    st.info("🚧 구현 예정: 감정 분석 및 키워드 추출")

    # 샘플 감정 분석 결과
    sentiment_data = pd.DataFrame(
        {"감정": ["긍정", "중립", "부정"], "비율": [65, 25, 10]}
    )

    fig = px.pie(
        sentiment_data, values="비율", names="감정", title="샘플: 리뷰 감정 분포"
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def display_analysis_results(
    products_df, price_analyzer, review_analyzer, delivery_analyzer
):  # review_analyzer, delivery_analyzer 추가
    """분석 결과 대시보드 표시"""

    st.success("🎉 분석이 완료되었습니다!")

    # 요약 통계
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 상품 수", len(products_df))

    with col2:
        # price_analyzer에서 계산된 평균 가격 사용
        avg_price = price_analyzer.analyze_prices()["basic_stats"]["mean"]
        st.metric("평균 가격", f"₩{avg_price:,.0f}")

    with col3:
        total_reviews = (
            products_df["review_count"].sum()
            if "review_count" in products_df.columns
            else 0
        )
        st.metric("총 리뷰 수", f"{total_reviews:,}")

    with col4:
        # is_rocket 컬럼이 있는지 확인
        if "is_rocket" in products_df.columns and not products_df.empty:
            rocket_ratio = (products_df["is_rocket"].sum() / len(products_df)) * 100
            st.metric("로켓배송 비율", f"{rocket_ratio:.1f}%")
        else:
            st.metric("로켓배송 비율", "N/A")

    # 4행 2열 그리드 대시보드
    st.markdown("---")
    st.markdown("## 📊 상세 분석 대시보드")

    # 1행: 가격 분석 | 리뷰수 분석
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        display_price_analysis_grid(price_analyzer)
    with col1_2:
        display_review_count_analysis(review_analyzer)  # review_analyzer 전달

    st.markdown("---")

    # 2행: 상위10 판매량 | 조회수 분석
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        display_top10_sales_placeholder()
    with col2_2:
        display_view_count_analysis()

    st.markdown("---")

    # 3행: 판매형태 분석 | 광고 분석
    col3_1, col3_2 = st.columns(2)
    with col3_1:
        display_sales_type_analysis(delivery_analyzer)  # delivery_analyzer 전달
    with col3_2:
        display_ads_analysis_placeholder()

    st.markdown("---")

    # 4행: 검색 트렌드 | 리뷰 분석
    col4_1, col4_2 = st.columns(2)
    with col4_1:
        display_search_trends_placeholder()
    with col4_2:
        display_review_analysis_placeholder()

    st.markdown("---")

    # 상품 목록 (전체 너비로 표시)
    st.markdown("## 📋 상품 목록")
    st.dataframe(products_df, use_container_width=True)


def analyze_data(search_html, product_html, wings_html, ads_html, trends_html):
    """메인 분석 실행 함수"""

    progress_bar = st.progress(0, text="분석 준비 중...")

    try:
        # 1단계: HTML 파싱
        progress_bar.progress(20, text="📄 HTML 파일 파싱 중...")
        search_content = read_html_file(search_html)
        product_content = read_html_file(product_html)

        # 2단계: 데이터 추출
        progress_bar.progress(40, text="🔍 상품 데이터 추출 중...")
        products_df = parse_coupang_search(search_content)
        product_details = parse_product_detail(product_content)

        # --- 디버깅 로그 추가 ---
        if (
            not products_df.empty
            and "name" in products_df.columns
            and "price" in products_df.columns
        ):
            logging.info(
                f"PriceAnalyzer로 전달될 DataFrame:\n{products_df[['name', 'price']].to_string()}"
            )
        else:
            logging.warning(
                "PriceAnalyzer로 전달될 DataFrame이 비어있거나 필수 컬럼이 없습니다."
            )
        # --------------------

        # 3단계: 데이터 분석
        progress_bar.progress(60, text="📊 데이터 분석 중...")
        price_analyzer = PriceAnalyzer(products_df)
        review_analyzer = ReviewAnalyzer(products_df)  # ReviewAnalyzer 초기화
        delivery_analyzer = DeliveryAnalyzer(products_df)  # DeliveryAnalyzer 초기화

        # 4단계: 결과 시각화
        progress_bar.progress(80, text="📈 결과 시각화 중...")
        display_analysis_results(
            products_df, price_analyzer, review_analyzer, delivery_analyzer
        )  # review_analyzer, delivery_analyzer 전달

        progress_bar.progress(100, text="✅ 분석 완료!")

        # 세션 상태에 결과 저장
        st.session_state["analysis_complete"] = True
        st.session_state["products_df"] = products_df

    except Exception as e:
        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
        logging.error(f"분석 중 오류: {e}", exc_info=True)
        st.stop()


# 사이드바 - 파일 업로드
with st.sidebar:
    st.header("📁 파일 업로드")

    search_html = st.file_uploader(
        "쿠팡 검색 결과 HTML (필수)", type=["html", "htm"], key="search_html"
    )

    product_html = st.file_uploader(
        "상품 상세 페이지 HTML (필수)", type=["html", "htm"], key="product_html"
    )

    wings_html = st.file_uploader(
        "쿠팡윙스 HTML (선택)", type=["html", "htm"], key="wings_html"
    )

    ads_html = st.file_uploader(
        "광고센터 HTML (선택)", type=["html", "htm"], key="ads_html"
    )

    trends_html = st.file_uploader(
        "네이버 트렌드 HTML (선택)", type=["html", "htm"], key="trends_html"
    )

# 분석 시작 버튼
if search_html and product_html:
    if st.button("🚀 분석 시작", type="primary"):
        analyze_data(search_html, product_html, wings_html, ads_html, trends_html)
else:
    st.info("🔺 필수 파일(검색 결과 + 상품 상세)을 업로드해주세요")
