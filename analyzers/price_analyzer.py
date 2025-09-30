import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import logging


class PriceAnalyzer:
    def __init__(self, products_df):
        """PriceAnalyzer 초기화

        Args:
            products_df (pd.DataFrame): CoupangParser를 통해 파싱된 상품 데이터프레임
        """
        self.products_df = products_df.copy()
        # 'price' 컬럼이 없거나 비어있는 경우, 0으로 채워진 컬럼 생성
        if (
            "price" not in self.products_df.columns
            or self.products_df["price"].isnull().all()
        ):
            self.products_df["price"] = 0
        else:
            # NaN 값을 0으로 채우고 정수형으로 변환
            self.products_df["price"] = self.products_df["price"].fillna(0).astype(int)

        # --- 디버깅 로그 추가 ---
        logging.info(
            f"PriceAnalyzer 초기화 완료. 가격 컬럼 요약:\n{self.products_df['price'].describe().to_string()}"
        )
        # --------------------

    def analyze_prices(self):
        """가격 데이터 종합 분석"""
        # 가격이 0보다 큰 유효한 데이터만 필터링
        prices = self.products_df["price"][self.products_df["price"] > 0].dropna()

        # 분석할 가격 데이터가 없는 경우 None 반환
        if prices.empty:
            return {
                "basic_stats": self._calculate_basic_stats(prices),
                "price_distribution": self._analyze_price_distribution(prices),
            }

        analysis = {
            "basic_stats": self._calculate_basic_stats(prices),
            "price_distribution": self._analyze_price_distribution(prices),
            # 'rocket_vs_normal': self._compare_rocket_prices(), # 다음 단계에서 구현
            # 'seller_analysis': self._analyze_by_seller(), # 다음 단계에서 구현
            # 'discount_analysis': self._analyze_discounts() # 다음 단계에서 구현
        }

        return analysis

    def _calculate_basic_stats(self, prices):
        """기본 통계 계산"""
        if prices.empty:
            return {
                "count": 0,
                "mean": 0,
                "median": 0,
                "std": 0,
                "min": 0,
                "max": 0,
                "q25": 0,
                "q75": 0,
            }

        return {
            "count": len(prices),
            "mean": prices.mean(),
            "median": prices.median(),
            "std": prices.std(),
            "min": prices.min(),
            "max": prices.max(),
            "q25": prices.quantile(0.25),
            "q75": prices.quantile(0.75),
        }

    def _analyze_price_distribution(self, prices):
        """가격 분포 분석"""
        if prices.empty:
            return pd.Series(dtype=int)

        # 가격 구간 설정
        bins = [0, 10000, 30000, 50000, 100000, 200000, float("inf")]
        labels = [
            "1만원 미만",
            "1-3만원",
            "3-5만원",
            "5-10만원",
            "10-20만원",
            "20만원 이상",
        ]

        price_ranges = pd.cut(
            prices, bins=bins, labels=labels, right=False, include_lowest=True
        )
        distribution = price_ranges.value_counts().sort_index()

        return distribution

    def create_product_price_bar_chart(self):
        """상품별 가격 막대 차트 생성"""
        price_data = self.products_df[self.products_df["price"] > 0].copy()
        if price_data.empty:
            return go.Figure().update_layout(title="상품별 가격 정보 (데이터 없음)")

        # 가격 기준 오름차순 정렬
        price_data = price_data.sort_values(by="price", ascending=True).reset_index(
            drop=True
        )

        stats = self.analyze_prices()["basic_stats"]
        median_price = stats["median"]  # 중간값 사용
        min_price = stats["min"]
        max_price = stats["max"]

        # 색상 결정
        colors = []
        for price in price_data["price"]:
            if price == min_price:
                colors.append("blue")
            elif price == max_price:
                colors.append("red")
            elif price == median_price:  # 중간값 비교
                colors.append("green")
            else:
                colors.append("grey")

        price_data["name"] = price_data["name"].str.wrap(20)  # 긴 상품명 줄바꿈

        fig = go.Figure(
            go.Bar(
                x=price_data.index,  # X축을 고유한 인덱스로 변경
                y=price_data["price"],
                marker_color=colors,
                text=price_data["price"].apply(lambda x: f"₩{x:,.0f}"),
                textposition="auto",
                customdata=price_data["name"],  # hovertemplate에서 사용할 데이터
                hovertemplate="<b>%{customdata}</b><br>가격: %{y:,.0f}원<extra></extra>",
            )
        )

        fig.update_layout(
            title_text=f"상품별 가격 분포 (중간값: ₩{median_price:,.0f}, 범위: ₩{min_price:,.0f} ~ ₩{max_price:,.0f})",  # 제목 변경
            xaxis_title="상품명 (가격 오름차순)",
            yaxis_title="가격 (원)",
            height=500,
        )

        # X축 상품명 레이블 제거
        fig.update_xaxes(showticklabels=False)

        return fig

    def create_price_boxplot(self):
        """가격 분포 Box Plot 생성"""
        prices = self.products_df["price"][self.products_df["price"] > 0].dropna()

        if prices.empty:
            return go.Figure().update_layout(
                title="가격 분포 Box Plot (데이터 없음)",
                height=200,
                annotations=[
                    {
                        "text": "데이터 없음",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                    }
                ],
            )

        fig = px.box(
            self.products_df[self.products_df["price"] > 0],
            x="price",
            title="가격 분포 Box Plot",
            points="all",  # 모든 데이터 포인트 표시
            hover_data=["name"],  # 마우스 올렸을 때 상품명 표시
        )
        fig.update_layout(height=200, yaxis_title="")
        return fig
