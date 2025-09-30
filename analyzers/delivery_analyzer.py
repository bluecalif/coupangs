import pandas as pd
import plotly.graph_objects as go
import logging


class DeliveryAnalyzer:
    def __init__(self, products_df):
        """배송 타입 분석기 초기화"""
        self.products_df = products_df

        # delivery_type 컬럼이 없거나 비어있으면 기본값 설정
        if "delivery_type" not in self.products_df.columns:
            logging.warning(
                "delivery_type 컬럼이 없습니다. '일반배송'으로 기본값 설정합니다."
            )
            self.products_df["delivery_type"] = "일반배송"

        self.stats = self._calculate_delivery_stats()

    def _calculate_delivery_stats(self):
        """배송 타입별 통계 계산"""
        delivery_counts = self.products_df["delivery_type"].value_counts()
        total = len(self.products_df)

        stats = {
            "counts": delivery_counts.to_dict(),
            "percentages": (delivery_counts / total * 100).to_dict(),
            "total": total,
        }

        logging.info(f"배송 타입 통계: {stats}")
        return stats

    def create_delivery_pie_chart(self):
        """배송 타입 비율 스택 막대 그래프 생성 (텍스트 없이)"""
        if self.stats["total"] == 0:
            logging.warning("분석할 데이터가 없습니다.")
            return None

        # 배송 타입 순서 정의 (로켓 -> 그로스 -> 일반)
        delivery_order = ["로켓배송", "그로스", "일반배송"]
        colors_map = {
            "로켓배송": "#E63946",  # 빨강
            "그로스": "#F77F00",  # 주황
            "일반배송": "#6C757D",  # 회색
        }

        fig = go.Figure()

        # 각 배송 타입별로 Bar 추가 (텍스트 제거)
        for delivery_type in delivery_order:
            count = self.stats["counts"].get(delivery_type, 0)
            percentage = self.stats["percentages"].get(delivery_type, 0)

            fig.add_trace(
                go.Bar(
                    y=[""],
                    x=[count],
                    name=delivery_type,
                    orientation="h",
                    marker=dict(color=colors_map.get(delivery_type, "#6C757D")),
                    hovertemplate=f"<b>{delivery_type}</b><br>개수: {count}<br>비율: {percentage:.1f}%<extra></extra>",
                )
            )

        fig.update_layout(
            barmode="stack",
            height=80,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return fig
