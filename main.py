import streamlit as st
import pandas as pd
import plotly.express as px
# from parsers.coupang_parser import CoupangParser
# from analyzers.price_analyzer import PriceAnalyzer

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

def analyze_data(search_html, product_html, wings_html, ads_html, trends_html):
    """메인 분석 실행 함수 (현재는 비어 있음)"""
    st.info("분석 기능이 구현될 예정입니다.")
    pass

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
