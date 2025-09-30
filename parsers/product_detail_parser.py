from bs4 import BeautifulSoup
import pandas as pd
import re
import logging


class ProductDetailParser:
    def parse_product_detail(self, html_content):
        """상품 상세 페이지에서 리뷰, 스펙 등 추출"""
        if not html_content:
            return {}

        soup = BeautifulSoup(html_content, "html.parser")

        return {
            "reviews": self._extract_reviews(soup),
            # 'specifications': self._extract_specifications(soup),
            # 'images': self._extract_images(soup),
            # 'sales_info': self._extract_sales_info(soup),
            # 'qna': self._extract_qna(soup)
        }

    def _extract_reviews(self, soup):
        """리뷰 데이터 추출"""
        reviews = []
        # 정확한 선택자로 수정
        review_items = soup.find_all(
            "article",
            class_=["sdp-review__article__list", "js_reviewArticleReviewList"],
        )

        logging.info(f"발견된 리뷰 수: {len(review_items)}")

        for item in review_items:
            try:
                review = {
                    "rating": self._extract_review_rating(item),
                    "content": self._extract_review_content(item),
                    "date": self._extract_review_date(item),
                    "helpful_count": self._extract_helpful_count(item),
                    "product_info": self._extract_product_info(item),
                }
                reviews.append(review)
            except Exception as e:
                logging.error(f"리뷰 파싱 중 오류: {e}")
                continue

        return pd.DataFrame(reviews)

    def _extract_review_rating(self, item):
        """리뷰 평점 추출"""
        rating_elem = item.find(
            "div", class_="sdp-review__article__list__info__product-info__star-orange"
        )
        if rating_elem:
            style = rating_elem.get("style", "")
            width_match = re.search(r"width:\s*(\d+(?:\.\d+)?)%", style)
            if width_match:
                # 100% = 5점 기준으로 변환
                return round(float(width_match.group(1)) / 20, 1)
        return 0.0

    def _extract_review_content(self, item):
        """리뷰 내용 추출"""
        content_elem = item.find(
            "div", class_="sdp-review__article__list__review__content"
        )
        return content_elem.get_text(strip=True) if content_elem else None

    def _extract_review_date(self, item):
        return None

    def _extract_helpful_count(self, item):
        return 0

    def _extract_product_info(self, item):
        return None
