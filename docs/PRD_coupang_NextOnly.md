# 쿠팡 카피캣 PRD - 프론트엔드 전용 버전

## 🎯 프로젝트 개요

### 제품명
**CoupangCopyCat Client** - 클라이언트 사이드 전자상거래 분석 도구

### 제품 비전
사용자 브라우저에서 모든 처리가 이루어지는 **Zero Server** 방식의 쿠팡 시장 분석 대시보드

### 핵심 가치 제안
- **즉시 실행**: 서버 없이 브라우저에서 바로 분석
- **완전 무료**: 서버 비용 Zero, 완전 무료 서비스
- **데이터 보안**: HTML 파일이 서버로 전송되지 않음
- **오프라인 작업**: 인터넷 연결 없이도 분석 가능

---

## 🏗 아키텍처 설계

### 전체 구조 (Single Page Application)
```
┌─────────────────────────────────────┐
│           브라우저 (사용자)          │
├─────────────────────────────────────┤
│  Next.js App (Static Generation)   │
│  ├── 파일 업로드 & 읽기             │
│  ├── HTML 파싱 (클라이언트)         │
│  ├── 데이터 분석 & 차트             │
│  └── 결과 표시                     │
├─────────────────────────────────────┤
│          정적 파일 배포             │
│    (Vercel/Netlify/GitHub Pages)   │
└─────────────────────────────────────┘
```

### 기술 스택 간소화
- **프론트엔드**: Next.js 14 (Static Export)
- **파일 처리**: FileReader API (브라우저 내장)
- **HTML 파싱**: DOMParser + 정규식
- **차트**: Recharts
- **스타일링**: Tailwind CSS
- **배포**: Vercel Static Export

---

## 📋 기능 요구사항

### 1. 파일 업로드 및 처리

#### 1.1 드래그앤드롭 파일 업로드
```typescript
interface FileUploadSystem {
  searchHtml: File;        // 쿠팡 검색 결과 HTML (필수)
  productDetailHtml: File; // 상품 상세 페이지 HTML (필수)
  wingsHtml?: File;        // 쿠팡윙스 HTML (선택)
  adsHtml?: File;          // 광고센터 HTML (선택)
  trendsHtml?: File;       // 네이버 트렌드 HTML (선택)
}
```

#### 1.2 클라이언트 사이드 파일 읽기
```javascript
// FileReader API 활용
const readHTMLFile = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.readAsText(file, 'utf-8');
  });
};
```

### 2. HTML 파싱 엔진 (클라이언트 사이드)

#### 2.1 쿠팡 검색 결과 파싱
```javascript
class CoupangParser {
  parseSearchHTML(htmlContent) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    const products = [];
    const productItems = doc.querySelectorAll('li[data-product-id]');
    
    productItems.forEach(item => {
      const product = {
        id: item.getAttribute('data-product-id'),
        name: item.querySelector('.name')?.textContent?.trim(),
        price: this.extractPrice(item),
        reviewCount: this.extractReviewCount(item),
        rating: this.extractRating(item),
        isRocket: item.querySelector('.rocket')?.length > 0,
        imageUrl: item.querySelector('img')?.src,
        seller: this.extractSeller(item)
      };
      products.push(product);
    });
    
    return products;
  }
  
  extractPrice(element) {
    const priceText = element.querySelector('.price-value')?.textContent;
    return priceText ? parseInt(priceText.replace(/[^\d]/g, '')) : 0;
  }
  
  extractReviewCount(element) {
    const reviewText = element.querySelector('.rating-total-count')?.textContent;
    return reviewText ? parseInt(reviewText.replace(/[^\d]/g, '')) : 0;
  }
}
```

#### 2.2 상품 상세 페이지 파싱
```javascript
class ProductDetailParser {
  parseProductDetail(htmlContent) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    return {
      productInfo: this.extractProductInfo(doc),
      reviews: this.extractReviews(doc),
      specifications: this.extractSpecs(doc),
      images: this.extractImages(doc),
      salesData: this.extractSalesData(doc)
    };
  }
  
  extractReviews(doc) {
    const reviews = [];
    const reviewElements = doc.querySelectorAll('.sdp-review__article__list');
    
    reviewElements.forEach(element => {
      reviews.push({
        rating: this.extractReviewRating(element),
        content: element.querySelector('.sdp-review__article__list__review__content')?.textContent,
        date: element.querySelector('.sdp-review__article__list__info__product-info__reg-date')?.textContent,
        helpful: this.extractHelpfulCount(element)
      });
    });
    
    return reviews;
  }
}
```

### 3. 데이터 분석 엔진 (클라이언트 사이드)

#### 3.1 가격 분석
```javascript
class PriceAnalyzer {
  analyzePrices(products) {
    const prices = products.map(p => p.price).filter(p => p > 0);
    
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
      average: prices.reduce((a, b) => a + b, 0) / prices.length,
      median: this.calculateMedian(prices),
      distribution: this.createPriceDistribution(prices),
      chartData: this.preparePriceChartData(products)
    };
  }
  
  createPriceDistribution(prices) {
    const ranges = [
      { label: '1만원 미만', min: 0, max: 10000 },
      { label: '1-5만원', min: 10000, max: 50000 },
      { label: '5-10만원', min: 50000, max: 100000 },
      { label: '10만원 이상', min: 100000, max: Infinity }
    ];
    
    return ranges.map(range => ({
      label: range.label,
      count: prices.filter(p => p >= range.min && p < range.max).length,
      percentage: (prices.filter(p => p >= range.min && p < range.max).length / prices.length) * 100
    }));
  }
}
```

#### 3.2 리뷰 분석 (감정 분석)
```javascript
class ReviewAnalyzer {
  analyzeReviews(reviews) {
    return {
      totalCount: reviews.length,
      averageRating: this.calculateAverageRating(reviews),
      sentimentAnalysis: this.performSentimentAnalysis(reviews),
      keywordExtraction: this.extractKeywords(reviews),
      ratingDistribution: this.createRatingDistribution(reviews)
    };
  }
  
  performSentimentAnalysis(reviews) {
    // 간단한 키워드 기반 감정 분석
    const positiveKeywords = ['좋', '만족', '추천', '훌륭', '완벽', '빠름'];
    const negativeKeywords = ['나쁨', '불만', '안좋', '느림', '문제', '별로'];
    
    let positive = 0, negative = 0, neutral = 0;
    
    reviews.forEach(review => {
      const content = review.content?.toLowerCase() || '';
      const positiveScore = positiveKeywords.filter(k => content.includes(k)).length;
      const negativeScore = negativeKeywords.filter(k => content.includes(k)).length;
      
      if (positiveScore > negativeScore) positive++;
      else if (negativeScore > positiveScore) negative++;
      else neutral++;
    });
    
    return {
      positive: (positive / reviews.length) * 100,
      negative: (negative / reviews.length) * 100,
      neutral: (neutral / reviews.length) * 100
    };
  }
}
```

### 4. 네이버 트렌드 파싱
```javascript
class NaverTrendsParser {
  parseTrendsHTML(htmlContent) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    // 네이버 데이터랩의 차트 데이터는 보통 script 태그 내 JSON으로 있음
    const scripts = doc.querySelectorAll('script');
    let trendsData = null;
    
    scripts.forEach(script => {
      const content = script.textContent;
      if (content.includes('chartData') || content.includes('trendsData')) {
        // 정규식으로 JSON 데이터 추출
        const jsonMatch = content.match(/(?:chartData|trendsData)\s*=\s*(\[.*?\]);/);
        if (jsonMatch) {
          trendsData = JSON.parse(jsonMatch[1]);
        }
      }
    });
    
    return this.processTrendsData(trendsData);
  }
}
```

---

## 🎨 프론트엔드 설계

### 5. 컴포넌트 구조

#### 5.1 프로젝트 구조
```
src/
├── app/
│   ├── page.tsx                 # 메인 페이지
│   ├── layout.tsx              # 레이아웃
│   └── globals.css             # 전역 스타일
├── components/
│   ├── FileUpload/
│   │   ├── FileDropzone.tsx    # 드래그앤드롭 업로드
│   │   ├── FileList.tsx        # 업로드된 파일 목록
│   │   └── UploadGuide.tsx     # 사용자 가이드
│   ├── Analysis/
│   │   ├── AnalysisProgress.tsx # 분석 진행상황
│   │   └── ResultSummary.tsx   # 분석 결과 요약
│   ├── Charts/
│   │   ├── PriceChart.tsx      # 가격 분포 차트
│   │   ├── ReviewChart.tsx     # 리뷰 분석 차트
│   │   ├── SalesChart.tsx      # 판매량 추정 차트
│   │   ├── TrendChart.tsx      # 트렌드 차트
│   │   └── SentimentChart.tsx  # 감정 분석 차트
│   └── UI/
│       ├── Button.tsx
│       ├── Card.tsx
│       └── LoadingSpinner.tsx
├── lib/
│   ├── parsers/
│   │   ├── coupang-parser.ts   # 쿠팡 HTML 파싱
│   │   ├── product-parser.ts   # 상품 상세 파싱
│   │   ├── wings-parser.ts     # 윙스 파싱
│   │   └── naver-parser.ts     # 네이버 트렌드 파싱
│   ├── analyzers/
│   │   ├── price-analyzer.ts   # 가격 분석
│   │   ├── review-analyzer.ts  # 리뷰 분석
│   │   └── trend-analyzer.ts   # 트렌드 분석
│   ├── utils/
│   │   ├── file-reader.ts      # 파일 읽기 유틸
│   │   ├── data-validator.ts   # 데이터 검증
│   │   └── chart-utils.ts      # 차트 데이터 변환
│   └── types/
│       ├── product.ts          # 상품 타입 정의
│       ├── review.ts           # 리뷰 타입 정의
│       └── analysis.ts         # 분석 결과 타입
├── hooks/
│   ├── useFileUpload.ts        # 파일 업로드 훅
│   ├── useHTMLParser.ts        # HTML 파싱 훅
│   └── useAnalysis.ts          # 분석 실행 훅
└── styles/
    └── components.css          # 컴포넌트 스타일
```

#### 5.2 메인 페이지 구성
```typescript
// app/page.tsx
'use client';

import { useState } from 'react';
import { FileDropzone } from '@/components/FileUpload/FileDropzone';
import { AnalysisProgress } from '@/components/Analysis/AnalysisProgress';
import { DashboardGrid } from '@/components/Dashboard/DashboardGrid';
import { useAnalysis } from '@/hooks/useAnalysis';

export default function Home() {
  const [files, setFiles] = useState<UploadedFiles>({});
  const { analysisData, isAnalyzing, startAnalysis } = useAnalysis();

  const handleFilesUploaded = async (uploadedFiles: UploadedFiles) => {
    setFiles(uploadedFiles);
    await startAnalysis(uploadedFiles);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            쿠팡 카피캣 - 시장 분석 도구
          </h1>
          <p className="text-gray-600 mt-1">
            HTML 파일을 업로드하여 즉시 시장 분석 결과를 확인하세요
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!analysisData ? (
          <div className="max-w-2xl mx-auto">
            <FileDropzone onFilesUploaded={handleFilesUploaded} />
            {isAnalyzing && <AnalysisProgress />}
          </div>
        ) : (
          <DashboardGrid data={analysisData} />
        )}
      </main>
    </div>
  );
}
```

#### 5.3 파일 업로드 컴포넌트
```typescript
// components/FileUpload/FileDropzone.tsx
'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileDropzoneProps {
  onFilesUploaded: (files: UploadedFiles) => void;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({ onFilesUploaded }) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFiles>({});

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = { ...uploadedFiles };
    
    acceptedFiles.forEach(file => {
      const fileName = file.name.toLowerCase();
      
      if (fileName.includes('search') || fileName.includes('검색')) {
        newFiles.searchHtml = file;
      } else if (fileName.includes('product') || fileName.includes('상품')) {
        newFiles.productDetailHtml = file;
      } else if (fileName.includes('wings') || fileName.includes('윙스')) {
        newFiles.wingsHtml = file;
      } else if (fileName.includes('ads') || fileName.includes('광고')) {
        newFiles.adsHtml = file;
      } else if (fileName.includes('trend') || fileName.includes('트렌드')) {
        newFiles.trendsHtml = file;
      }
    });
    
    setUploadedFiles(newFiles);
  }, [uploadedFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/html': ['.html', '.htm']
    },
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const canAnalyze = uploadedFiles.searchHtml && uploadedFiles.productDetailHtml;

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
      >
        <input {...getInputProps()} />
        <div className="space-y-2">
          <div className="text-4xl">📁</div>
          <div className="text-lg font-medium">
            {isDragActive ? 'HTML 파일을 여기에 놓아주세요' : 'HTML 파일을 드래그하거나 클릭하여 업로드'}
          </div>
          <div className="text-sm text-gray-500">
            쿠팡 검색결과 HTML (필수) + 상품상세 HTML (필수) + 기타 (선택)
          </div>
        </div>
      </div>

      {Object.keys(uploadedFiles).length > 0 && (
        <FileList files={uploadedFiles} onRemove={(key) => {
          const newFiles = { ...uploadedFiles };
          delete newFiles[key];
          setUploadedFiles(newFiles);
        }} />
      )}

      {canAnalyze && (
        <button
          onClick={() => onFilesUploaded(uploadedFiles)}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          📊 분석 시작하기
        </button>
      )}
    </div>
  );
};
```

---

## 🔧 기술 구현

### 6. 파일 읽기 및 파싱 훅

```typescript
// hooks/useHTMLParser.ts
import { useState, useCallback } from 'react';
import { CoupangParser } from '@/lib/parsers/coupang-parser';
import { ProductDetailParser } from '@/lib/parsers/product-parser';

export const useHTMLParser = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parseFiles = useCallback(async (files: UploadedFiles) => {
    setIsLoading(true);
    setError(null);

    try {
      const results: ParsedData = {
        products: [],
        productDetails: null,
        trends: null,
        ads: null
      };

      // 필수 파일 파싱
      if (files.searchHtml) {
        const htmlContent = await readFileAsText(files.searchHtml);
        const parser = new CoupangParser();
        results.products = parser.parseSearchHTML(htmlContent);
      }

      if (files.productDetailHtml) {
        const htmlContent = await readFileAsText(files.productDetailHtml);
        const parser = new ProductDetailParser();
        results.productDetails = parser.parseProductDetail(htmlContent);
      }

      // 선택적 파일 파싱
      if (files.trendsHtml) {
        const htmlContent = await readFileAsText(files.trendsHtml);
        const parser = new NaverTrendsParser();
        results.trends = parser.parseTrendsHTML(htmlContent);
      }

      return results;
    } catch (err) {
      setError(err instanceof Error ? err.message : '파싱 중 오류가 발생했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = () => reject(new Error('파일 읽기 실패'));
      reader.readAsText(file, 'utf-8');
    });
  };

  return { parseFiles, isLoading, error };
};
```

### 7. 분석 실행 훅

```typescript
// hooks/useAnalysis.ts
import { useState } from 'react';
import { useHTMLParser } from './useHTMLParser';
import { PriceAnalyzer } from '@/lib/analyzers/price-analyzer';
import { ReviewAnalyzer } from '@/lib/analyzers/review-analyzer';

export const useAnalysis = () => {
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const { parseFiles } = useHTMLParser();

  const startAnalysis = async (files: UploadedFiles) => {
    setIsAnalyzing(true);

    try {
      // 1단계: HTML 파싱
      const parsedData = await parseFiles(files);

      // 2단계: 데이터 분석
      const priceAnalyzer = new PriceAnalyzer();
      const reviewAnalyzer = new ReviewAnalyzer();

      const priceAnalysis = priceAnalyzer.analyzePrices(parsedData.products);
      const reviewAnalysis = parsedData.productDetails?.reviews ? 
        reviewAnalyzer.analyzeReviews(parsedData.productDetails.reviews) : null;

      // 3단계: 차트 데이터 준비
      const result: AnalysisResult = {
        summary: {
          totalProducts: parsedData.products.length,
          averagePrice: priceAnalysis.average,
          totalReviews: reviewAnalysis?.totalCount || 0,
          averageRating: reviewAnalysis?.averageRating || 0
        },
        charts: {
          priceDistribution: priceAnalysis.chartData,
          reviewSentiment: reviewAnalysis?.sentimentAnalysis,
          trends: parsedData.trends?.chartData
        },
        tables: {
          products: parsedData.products,
          topKeywords: reviewAnalysis?.keywordExtraction
        }
      };

      setAnalysisData(result);
    } catch (error) {
      console.error('분석 실패:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return { analysisData, isAnalyzing, startAnalysis };
};
```

---

## 🚀 배포 및 운영

### 8. 정적 사이트 배포

#### 8.1 Next.js 정적 빌드 설정
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // 정적 사이트 생성
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'dist',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/coupang-copycat' : '',
  images: {
    unoptimized: true  // 정적 빌드에서 이미지 최적화 비활성화
  }
};

module.exports = nextConfig;
```

#### 8.2 배포 옵션
**Vercel (추천)**:
```bash
npm run build
# Vercel CLI로 배포 또는 GitHub 연동
```

**Netlify**:
```bash
npm run build
# 빌드된 dist 폴더를 Netlify에 업로드
```

**GitHub Pages**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

---

## 📊 개발 일정

### 9. 마일스톤 (프론트엔드 전용)

#### Phase 1: 기본 구조 (3-4일) ⚡
- [x] Next.js 프로젝트 설정
- [x] 파일 업로드 UI 컴포넌트
- [x] HTML 파일 읽기 기능
- [x] 기본 쿠팡 HTML 파싱 엔진

#### Phase 2: 분석 기능 (4-5일)
- [ ] 가격 분석 엔진
- [ ] 리뷰 분석 엔진 (감정 분석)
- [ ] 기본 차트 컴포넌트 (가격/리뷰)
- [ ] 분석 결과 대시보드

#### Phase 3: 고급 기능 (3-4일)
- [ ] 네이버 트렌드 파싱
- [ ] 쿠팡윙스/광고센터 파싱
- [ ] 고급 차트 (트렌드, 감정분석)
- [ ] 데이터 내보내기 기능

#### Phase 4: 완성도 (2-3일)
- [ ] 반응형 디자인
- [ ] 사용자 가이드 및 도움말
- [ ] 성능 최적화
- [ ] 배포 및 테스트

**총 개발 기간**: **12-16일** (약 2-3주)

---

## 🎯 핵심 장점

### 프론트엔드 전용 방식의 혁신성

**🚀 개발 단순성**
- **하나의 프로젝트**: 백엔드/프론트엔드 분리 없음
- **실행 간단**: `npm run dev` 하나로 모든 것 실행
- **배포 간단**: 정적 파일만 업로드하면 완료

**💰 완전 무료**
- **서버 비용 Zero**: 정적 사이트 호스팅만 필요
- **Vercel 무료 플랜**: 무제한 배포 가능
- **운영비 Zero**: 서버 관리 불필요

**🔒 보안성 강화**
- **데이터 보안**: HTML이 서버로 전송되지 않음
- **개인정보 보호**: 모든 처리가 사용자 브라우저에서만
- **오프라인 작업**: 인터넷 연결 없이도 분석 가능

**⚡ 사용자 경험**
- **즉시 실행**: 서버 응답 대기 없음
- **빠른 분석**: 로컬 처리로 초고속 결과
- **안정성**: 서버 다운 없음

**🔧 개발 효율성**
- **디버깅 용이**: 모든 코드가 클라이언트에서 실행
- **테스트 간단**: 브라우저 개발자 도구로 모든 것 확인
- **확장 용이**: 새로운 파싱 엔진 추가 간단

---

## 🔮 향후 확장 계획

### 고급 기능 추가 (선택사항)
1. **PWA 변환**: 오프라인에서도 완전 작동
2. **Excel 내보내기**: 분석 결과를 Excel 파일로 저장
3. **템플릿 시스템**: 다양한 분석 리포트 템플릿
4. **브라우저 확장**: 쿠팡 페이지에서 바로 분석 실행
5. **API 연동**: 향후 공개 API 사용 시 확장 가능

이 방식으로 개발하면 **복잡한 백엔드 없이도** 강력한 분석 도구를 빠르게 만들 수 있습니다! 🎉