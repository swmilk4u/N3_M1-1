# SK하이닉스 / S&P 500 주가 트렌드 분석 (2025~2026)

> AI·HBM 수요 폭증 시대, 반도체 대표주 SK하이닉스와 글로벌 증시 S&P 500을 비교 분석합니다.

---

## 📁 프로젝트 구조

```
N3_M1-1_Data trend/
├── data/
│   ├── skhynix_2025_2026.csv    # SK하이닉스 일별 OHLCV
│   └── sp500_2025_2026.csv      # S&P 500 일별 OHLCV
├── images/
│   ├── 01_price_trend.png       # 정규화 가격 추이 비교
│   ├── 02_moving_average.png    # 이동평균 (20일·60일)
│   ├── 03_monthly_return.png    # 월별 수익률 히트맵
│   └── 04_decomposition.png     # 시계열 분해 (STL, 보너스)
├── 01_document/
│   └── N3_M1-1 과제미션.txt
├── analysis.ipynb               # 메인 분석 노트북
├── generate_analysis.py         # 데이터 수집·시각화 스크립트
├── REPORT.md                    # 전체 분석 리포트
├── requirements.txt             # 의존성 목록
└── README.md                    # 프로젝트 개요 (현재 파일)
```

---

## 🎯 분석 개요

| 항목 | 내용 |
|------|------|
| 분석 주제 | SK하이닉스 vs S&P 500 주가 트렌드 비교 |
| 데이터 출처 | Yahoo Finance (`yfinance`) |
| 분석 기간 | 2025-01-02 ~ 2026-08-21 |
| 데이터 포인트 | SK하이닉스 397거래일 / S&P 500 410거래일 |
| 분석 기법 | 이동평균·변화율·월별수익률집계·시계열분해(STL) |

---

## ⚙️ 실행 환경 & 설치

**Python 3.10 이상** 필요

```bash
# 의존성 설치
pip install -r requirements.txt
```

| 라이브러리 | 용도 |
|-----------|------|
| yfinance | Yahoo Finance 데이터 수집 |
| pandas | 데이터 처리·집계 |
| matplotlib | 시각화 |
| seaborn | 히트맵 시각화 |
| statsmodels | STL 시계열 분해 |
| numpy | 수치 계산 |

---

## 🚀 실행 방법

### 방법 1: Jupyter Notebook (권장)

```bash
jupyter notebook analysis.ipynb
```
- 셀을 **위에서 아래로 순서대로** 실행합니다.
- 데이터 수집 → 전처리 → 시각화 → 인사이트 순으로 구성되어 있습니다.

### 방법 2: 스크립트 직접 실행

```bash
# 데이터 수집 + 시각화 이미지 한 번에 생성
python generate_analysis.py
```

---

## 📊 분석 리포트

전체 분석 결과(질문·시각화·인사이트·결론·AI 사용 로그)는 **[REPORT.md](REPORT.md)** 를 확인하세요.

---

## 📋 데이터 출처 및 라이선스

- **출처**: Yahoo Finance (<https://finance.yahoo.com>)
- **수집 방법**: Python `yfinance` 라이브러리 (v0.2.51)
- **라이선스**: Yahoo Finance 이용약관에 따라 개인·교육 목적으로만 사용
- **면책 고지**: 본 분석은 투자 권유가 아니며, 과거 수익률이 미래를 보장하지 않습니다.
