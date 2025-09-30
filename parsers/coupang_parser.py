from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import os


class CoupangParser:
    def parse_search_html(self, html_content):
        """쿠팡 검색 결과 HTML에서 상품 정보 추출"""
        if not html_content:
            logging.warning("HTML 컨텐츠가 비어있어 파싱을 중단합니다.")
            return pd.DataFrame()

        soup = BeautifulSoup(html_content, "html.parser")  # lxml -> html.parser로 변경
        products = []

        # --- 디버깅 로그 수정 ---
        logging.info(f"BeautifulSoup 파싱 성공: HTML 구조 확인됨")
        if soup.body:
            logging.info(f"body 태그 발견: {soup.body.text[:100]}...")
        else:
            logging.info("body 태그 없음 (SPA 또는 특수 구조)")
        # --------------------

        # 상품 목록 파싱 (수정된 선택자)
        product_items = soup.find_all("li", class_="ProductUnit_productUnit__Qd6sv")

        logging.info(f"발견된 상품 수: {len(product_items)}")

        # HTML 구조는 logs/product_items.html 파일에서 확인 가능

        # --- 디버깅 로그 강화: 모든 상품의 HTML 구조를 기록 ---
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        with open(
            os.path.join(log_dir, "product_items.html"), "w", encoding="utf-8"
        ) as f:
            for i, item in enumerate(product_items):
                f.write(f"<!-- 상품 번호: {i+1} -->\n")
                f.write(item.prettify())
                f.write("\n\n")
        logging.info(
            "모든 상품의 HTML 구조를 logs/product_items.html 파일에 저장했습니다."
        )
        # -----------------------------------------------

        for item in product_items:
            try:
                product = {
                    "product_id": item.get("data-product-id"),
                    "name": self._extract_name(item),
                    "price": self._extract_price(item),
                    "original_price": self._extract_original_price(item),
                    "discount_rate": self._extract_discount_rate(item),
                    "review_count": self._extract_review_count(item),
                    "rating": self._extract_rating(item),
                    "is_rocket": self._is_rocket_delivery(item),
                    "delivery_type": self._extract_delivery_type(item),
                    "seller": self._extract_seller(item),
                    "image_url": self._extract_image_url(item),
                    "product_url": self._extract_product_url(item),
                }
                products.append(product)
            except Exception as e:
                # streamlit 앱에서는 st.warning을 사용하겠지만, 여기서는 print로 대체
                logging.error(f"상품 파싱 중 오류: {e}")
                continue

        products_df = pd.DataFrame(products)
        logging.info(f"파싱 완료. 총 {len(products)}개의 상품 데이터를 반환합니다.")
        if not products_df.empty and "review_count" in products_df.columns:
            logging.info("--- 파싱 직후 review_count 컬럼 요약 ---")
            logging.info(products_df["review_count"].describe())
            logging.info("-------------------------------------")
        if not products_df.empty and "delivery_type" in products_df.columns:
            logging.info("--- 파싱 직후 delivery_type 컬럼 요약 ---")
            logging.info(products_df["delivery_type"].value_counts())
            logging.info("-------------------------------------")
        return products_df

    def _extract_name(self, item):
        """상품명 추출 (img 태그의 alt 속성에서)"""
        name_elem = item.find("img")
        return name_elem.get("alt", "").strip() if name_elem else None

    def _extract_price(self, item):
        """가격 추출 (실제 HTML 구조 기반)"""
        # 1순위: 할인가 (빨간색 텍스트)
        price_elem = item.find("div", class_=re.compile(r"fw-text-red-700"))
        if price_elem and "원" in price_elem.get_text():
            price_text = price_elem.get_text(strip=True)
            price_digits = re.sub(r"[^\d]", "", price_text)
            if price_digits and len(price_digits) >= 3:
                logging.info(f"가격 추출 성공 (할인가): {price_digits}")
                return int(price_digits)

        # 2순위: 일반가 (회색 텍스트)
        price_elem = item.find("div", class_=re.compile(r"fw-text-bluegray-900"))
        if price_elem and "원" in price_elem.get_text():
            price_text = price_elem.get_text(strip=True)
            price_digits = re.sub(r"[^\d]", "", price_text)
            if price_digits and len(price_digits) >= 3:
                logging.info(f"가격 추출 성공 (일반가): {price_digits}")
                return int(price_digits)

        # 3순위: fw-font-bold와 원이 포함된 모든 div 태그
        price_elems = item.find_all("div", class_=re.compile(r"fw-font-bold"))
        for elem in price_elems:
            if "원" in elem.get_text():
                price_text = elem.get_text(strip=True)
                price_digits = re.sub(r"[^\d]", "", price_text)
                if price_digits and len(price_digits) >= 3:
                    logging.info(f"가격 추출 성공 (대체 방법): {price_digits}")
                    return int(price_digits)

        # 실패 시 디버깅 정보 로그
        logging.warning(
            f"가격 추출 실패. 상품 내 '원' 포함 텍스트: {[elem.get_text(strip=True) for elem in item.find_all(string=re.compile(r'원'))]}"
        )
        return 0

    def _extract_original_price(self, item):
        """원가 추출 (실제 HTML 구조 기반)"""
        # del 태그에서 원가 찾기
        original_price_elem = item.find("del", class_=re.compile(r"fw-line-through"))
        if original_price_elem and "원" in original_price_elem.get_text():
            price_text = original_price_elem.get_text(strip=True)
            price_digits = re.sub(r"[^\d]", "", price_text)
            if price_digits and len(price_digits) >= 3:
                logging.info(f"원가 추출 성공: {price_digits}")
                return int(price_digits)
        return 0

    def _extract_discount_rate(self, item):
        """할인율 추출 (실제 HTML 구조 기반)"""
        # % 기호를 포함한 span 태그 찾기
        discount_elems = item.find_all("span")
        for elem in discount_elems:
            text = elem.get_text(strip=True)
            if "%" in text:
                discount_text = text.replace("%", "").strip()
                if discount_text.isdigit():
                    logging.info(f"할인율 추출 성공: {discount_text}%")
                    return int(discount_text)
        return 0

    def _extract_review_count(self, item):
        """리뷰 수 추출"""
        review_elem = item.find("span", class_="ProductRating_ratingCount__R0Vhz")
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            review_digits = re.sub(r"[^\d]", "", review_text)
            if review_digits:
                logging.info(f"리뷰 수 추출 성공: {review_digits}")
                return int(review_digits)
        logging.warning(
            f"리뷰 수 추출 실패. HTML 일부: {str(item.find('div', class_='ProductRating_productRating__jjf7W'))[:200]}"
        )
        return 0

    def _extract_rating(self, item):
        """평점 추출"""
        rating_elem = item.find("em", class_="rating")
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            return float(rating_text) if rating_text else 0.0
        return 0.0

    def _is_rocket_delivery(self, item):
        """로켓배송 여부 (특정 클래스 존재 유무로 판단)"""
        return bool(
            item.find(
                lambda tag: tag.has_attr("class")
                and any("ProductUnit_rocket__" in s for s in tag["class"])
            )
        )

    def _extract_delivery_type(self, item):
        """배송 타입 추출 (로켓배송 / 그로스 / 일반배송)"""
        # 1순위: 로켓배송 체크 (logo_rocket_large)
        rocket_img = item.find("img", src=re.compile(r"logo_rocket_large"))
        if rocket_img:
            logging.info("배송 타입 추출 성공: 로켓배송")
            return "로켓배송"

        # 2순위: 그로스(판매자로켓) 체크 (logoRocketMerchant)
        gross_img = item.find("img", src=re.compile(r"logoRocketMerchant"))
        if gross_img:
            logging.info("배송 타입 추출 성공: 그로스")
            return "그로스"

        # 3순위: 일반배송 (배송 로고 없음)
        logging.info("배송 타입 추출 성공: 일반배송")
        return "일반배송"

    def _extract_seller(self, item):
        return None

    def _extract_image_url(self, item):
        """이미지 URL 추출 (img 태그의 src 속성에서)"""
        img_elem = item.find("img")
        return img_elem.get("src") if img_elem else None

    def _extract_product_url(self, item):
        """상품 URL 추출 (a 태그의 href 속성에서)"""
        url_elem = item.find("a")
        if url_elem:
            url = url_elem.get("href")
            # 상대 경로일 경우, coupang.com을 붙여줌
            if url and not url.startswith("http"):
                return "https://www.coupang.com" + url
            return url
        return None
