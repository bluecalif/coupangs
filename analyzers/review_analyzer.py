import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ReviewAnalyzer:
    def __init__(self, products_df):
        self.products_df = products_df.copy()
        if (
            "review_count" not in self.products_df.columns
            or self.products_df["review_count"].isnull().all()
        ):
            self.products_df["review_count"] = 0
        else:
            self.products_df["review_count"] = (
                self.products_df["review_count"].fillna(0).astype(int)
            )

    def analyze_reviews(self):
        """리뷰 데이터 종합 분석"""
        reviews = self.products_df["review_count"][
            self.products_df["review_count"] > 0
        ].dropna()
        if reviews.empty:
            return {
                "basic_stats": self._calculate_basic_stats(reviews),
                "distribution": self._analyze_distribution(reviews),
                "top_n": self.get_top_n_by_review(0),
            }

        analysis = {
            "basic_stats": self._calculate_basic_stats(reviews),
            "distribution": self._analyze_distribution(reviews),
            "top_n": self.get_top_n_by_review(10),
        }
        return analysis

    def _calculate_basic_stats(self, reviews):
        """기본 통계 계산"""
        if reviews.empty:
            return {"count": 0, "sum": 0, "mean": 0, "median": 0, "min": 0, "max": 0}

        return {
            "count": len(reviews),
            "sum": reviews.sum(),
            "mean": reviews.mean(),
            "median": reviews.median(),
            "min": reviews.min(),
            "max": reviews.max(),
        }

    def _analyze_distribution(self, reviews):
        """리뷰 수 분포 분석"""
        if reviews.empty:
            return pd.Series(dtype=int)

        bins = [0, 10, 50, 100, 500, 1000, float("inf")]
        labels = [
            "10개 미만",
            "10-50개",
            "50-100개",
            "100-500개",
            "500-1000개",
            "1000개 이상",
        ]
        review_ranges = pd.cut(reviews, bins=bins, labels=labels, right=False)
        return review_ranges.value_counts().sort_index()

    def get_top_n_by_review(self, n=10):
        """리뷰 수 기준 상위 N개 상품 반환"""
        return self.products_df.nlargest(n, "review_count")

    def create_top_reviews_chart(self, top_n_df):
        """리뷰 수 상위 상품 막대 차트 생성"""
        if top_n_df.empty:
            return go.Figure().update_layout(title="리뷰수 상위 상품 (데이터 없음)")

        fig = px.bar(
            top_n_df,
            x="review_count",
            y="name",
            orientation="h",
            title=f"리뷰수 상위 {len(top_n_df)}개 상품",
            labels={"review_count": "리뷰 수", "name": "상품명"},
            text="review_count",
        )
        fig.update_layout(height=300, yaxis={"categoryorder": "total ascending"})
        return fig

    def create_distribution_chart(self, distribution):
        """리뷰 수 분포 차트 생성"""
        if distribution.empty:
            return go.Figure().update_layout(title="리뷰수 분포 (데이터 없음)")

        fig = px.bar(
            x=distribution.index,
            y=distribution.values,
            title="리뷰수 구간별 상품 분포",
            labels={"x": "리뷰 수 구간", "y": "상품 수"},
            text=distribution.values,
        )
        fig.update_layout(height=300)
        return fig

    def create_product_review_bar_chart(self):
        """상품별 리뷰 수 막대 차트 생성 (가격 분석 차트와 동일한 포맷)"""
        review_data = self.products_df[self.products_df["review_count"] > 0].copy()
        if review_data.empty:
            return go.Figure().update_layout(title="상품별 리뷰 수 정보 (데이터 없음)")

        review_data = review_data.sort_values(
            by="review_count", ascending=True
        ).reset_index(drop=True)

        stats = self._calculate_basic_stats(review_data["review_count"])
        median_reviews = stats["median"]
        min_reviews = stats["min"]
        max_reviews = stats["max"]

        colors = []
        for count in review_data["review_count"]:
            if count == min_reviews:
                colors.append("blue")
            elif count == max_reviews:
                colors.append("red")
            elif count == median_reviews:
                colors.append("green")
            else:
                colors.append("grey")

        fig = go.Figure(
            go.Bar(
                x=review_data.index,
                y=review_data["review_count"],
                marker_color=colors,
                text=review_data["review_count"].apply(lambda x: f"{x:,.0f}개"),
                textposition="auto",
                customdata=review_data["name"],
                hovertemplate="<b>%{customdata}</b><br>리뷰 수: %{y:,.0f}개<extra></extra>",
            )
        )

        fig.update_layout(
            title_text=f"상품별 리뷰 수 분포 (중간값: {median_reviews:,.0f}개, 범위: {min_reviews:,.0f} ~ {max_reviews:,.0f}개)",
            xaxis_title="상품 (리뷰 수 오름차순)",
            yaxis_title="리뷰 수",
            height=500,
        )

        fig.update_xaxes(showticklabels=False)

        return fig
