"""
sync_report.py
==============
REPORT.md 내용이 변경되면 이 스크립트를 실행하세요.
README.md 안의 리포트 블록이 REPORT.md 내용으로 자동 갱신됩니다.

실행: python sync_report.py
"""

import re

# ── README 상단 고정 블록 (리포트 위) ──────────────────
README_TOP = """# SK하이닉스 / S&P 500 주가 트렌드 분석 (2025.1~2026.8)

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

## ⚙️ 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 노트북 실행 (위에서 아래로 순서대로 셀 실행)
jupyter notebook analysis.ipynb
```

---

## 📊 분석 리포트

"""

# ── README 하단 고정 블록 (리포트 아래) ───────────────
README_BOTTOM = """

---

## 📋 데이터 출처 및 라이선스

- **출처**: Yahoo Finance (<https://finance.yahoo.com>)
- **수집 방법**: Python `yfinance` 라이브러리 (v0.2.51)
- **라이선스**: Yahoo Finance 이용약관에 따라 개인·교육 목적으로만 사용
- **면책 고지**: 본 분석은 투자 권유가 아니며, 과거 수익률이 미래를 보장하지 않습니다.
"""

# ── REPORT.md 읽기 ────────────────────────────────────
with open('REPORT.md', 'r', encoding='utf-8') as f:
    report_content = f.read().strip()

# ── 접기/펼치기 블록으로 감싸기 ──────────────────────
report_block = f"""<details open>
<summary><b>📋 SK하이닉스 / S&P 500 주가 트렌드 분석 리포트 (2025.1~2026.8) — 클릭하여 접기/펼치기</b></summary>
<br>

{report_content}

</details>"""

# ── README.md 조합 후 저장 ────────────────────────────
readme_content = README_TOP + report_block + README_BOTTOM

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print('✅ README.md가 REPORT.md 내용으로 갱신되었습니다.')
print(f'   REPORT.md 크기: {len(report_content):,}자')
print(f'   README.md 크기: {len(readme_content):,}자')
