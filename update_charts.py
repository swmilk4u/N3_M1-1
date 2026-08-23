import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from statsmodels.tsa.seasonal import STL
import warnings
import os

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMG_DIR  = os.path.join(BASE_DIR, 'images')

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

COLOR_HYX  = '#E65100'   # SK하이닉스 (주황)
COLOR_SP   = '#1565C0'   # S&P 500 (블루)

# 데이터 로드
hyx = pd.read_csv(os.path.join(DATA_DIR, 'skhynix_2025_2026.csv'), index_col=0, parse_dates=True)
sp  = pd.read_csv(os.path.join(DATA_DIR, 'sp500_2025_2026.csv'),   index_col=0, parse_dates=True)

if isinstance(hyx.columns, pd.MultiIndex): hyx.columns = hyx.columns.get_level_values(0)
if isinstance(sp.columns,  pd.MultiIndex): sp.columns  = sp.columns.get_level_values(0)

hyx_close = hyx['Close'].dropna()
sp_close  = sp['Close'].dropna()

hyx_norm = hyx_close / hyx_close.iloc[0] * 100
sp_norm  = sp_close  / sp_close.iloc[0]  * 100
hyx_ma20 = hyx_close.rolling(20).mean()
hyx_ma60 = hyx_close.rolling(60).mean()
hyx_ret  = hyx_close.pct_change() * 100
sp_ret   = sp_close.pct_change()  * 100

def format_quarter(x, pos=None):
    dt = mdates.num2date(x)
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year} Q{q}\n({dt.month}월)"

# ----------------------------------------------------
# 1. 정규화 가격 추이 비교 (2단 분할: 상단 동일스케일 / 하단 이중축 줌인)
# ----------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# [상단: 동일 100 기준 정규화]
ax1.plot(hyx_norm.index, hyx_norm.values, color=COLOR_HYX, linewidth=2.0, label='SK하이닉스 (기준=100)')
ax1.plot(sp_norm.index,  sp_norm.values,  color=COLOR_SP,  linewidth=2.0, label='S&P 500 (기준=100)')
ax1.axhline(100, color='#888888', linewidth=1.0, linestyle='--', alpha=0.7)
ax1.set_title('[동일 스케일 비교] SK하이닉스 vs S&P 500 정규화 수익률 (2025.1 = 100)', fontsize=13, fontweight='bold', pad=10)
ax1.set_ylabel('정규화 지수 (시작가=100)', fontsize=11)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='upper left', fontsize=10)

ax1.annotate(f'SK하이닉스: +{hyx_norm.iloc[-1]-100:.1f}%\n(초고성장 랠리)', 
             xy=(hyx_norm.index[-1], hyx_norm.iloc[-1]), xytext=(-120, -25),
             textcoords='offset points', fontweight='bold', color=COLOR_HYX,
             arrowprops=dict(arrowstyle='->', color=COLOR_HYX, lw=1.5))
ax1.annotate(f'S&P 500: +{sp_norm.iloc[-1]-100:.1f}%\n(상대적으로 평평해 보임)', 
             xy=(sp_norm.index[-1], sp_norm.iloc[-1]), xytext=(-140, 20),
             textcoords='offset points', fontweight='bold', color=COLOR_SP,
             arrowprops=dict(arrowstyle='->', color=COLOR_SP, lw=1.5))

# [하단: 이중 Y축 개별 추세 비교 - S&P 500 추세 뚜렷하게 살리기]
ax2_twin = ax2.twinx()
line1 = ax2.plot(hyx_close.index, hyx_close.values, color=COLOR_HYX, linewidth=2.0, label='SK하이닉스 주가 (좌축, 원)')
line2 = ax2_twin.plot(sp_close.index, sp_close.values, color=COLOR_SP, linewidth=2.0, linestyle='-', label='S&P 500 지수 (우축, pt)')

ax2.set_title('[이중 축 스케일 보정] S&P 500의 우상향 흐름 및 세부 변동 상세 비교', fontsize=13, fontweight='bold', pad=10)
ax2.set_xlabel('기간 (분기 단위: Q1~Q4)', fontsize=11)
ax2.set_ylabel('SK하이닉스 (원)', fontsize=11, color=COLOR_HYX)
ax2_twin.set_ylabel('S&P 500 (포인트)', fontsize=11, color=COLOR_SP)

ax2.tick_params(axis='y', labelcolor=COLOR_HYX)
ax2_twin.tick_params(axis='y', labelcolor=COLOR_SP)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax2_twin.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax2.legend(lines, labels, loc='upper left', fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.5)

# 분기별(3개월) X축 눈금 설정
ax2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax2.xaxis.set_major_formatter(plt.FuncFormatter(format_quarter))
plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, '01_price_trend.png'), dpi=180, bbox_inches='tight')
plt.close()
print("01_price_trend.png OK")

# ----------------------------------------------------
# 2. 이동평균 (20일·60일) - 분기별 축 적용 및 구간 강조
# ----------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(hyx_close.index, hyx_close.values, color='#888888', linewidth=1.2, alpha=0.6, label='종가 (일별)')
ax.plot(hyx_ma20.index,  hyx_ma20.values,  color=COLOR_HYX, linewidth=2.2, label='20일 이동평균선 (단기 추세/1개월)')
ax.plot(hyx_ma60.index,  hyx_ma60.values,  color='#2E7D32', linewidth=2.2, label='60일 이동평균선 (중기 추세/1분기)')

cross = ((hyx_ma20 > hyx_ma60) & (hyx_ma20.shift(1) <= hyx_ma60.shift(1)))
dead  = ((hyx_ma20 < hyx_ma60) & (hyx_ma20.shift(1) >= hyx_ma60.shift(1)))

for d in hyx_close.index[cross]:
    ax.axvline(d, color='#1565C0', linewidth=1.5, alpha=0.7, linestyle='--')
for d in hyx_close.index[dead]:
    ax.axvline(d, color='#C62828', linewidth=1.5, alpha=0.7, linestyle='--')

ax.plot([], [], color='#1565C0', linestyle='--', label='골든크로스 (단기선>중기선 돌파)')
ax.plot([], [], color='#C62828', linestyle='--', label='데드크로스 (단기선<중기선 이탈)')

ax.set_title('SK하이닉스 — 주가 및 이동평균선(20일·60일) 추세 전환 분석', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('기간 (분기 단위: Q1~Q4)', fontsize=11)
ax.set_ylabel('주가 (원)', fontsize=11)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(plt.FuncFormatter(format_quarter))

ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, '02_moving_average.png'), dpi=180, bbox_inches='tight')
plt.close()
print("02_moving_average.png OK")

# ----------------------------------------------------
# 3. 분기별 & 월별 수익률 비교 (분기 바차트 + 월별 히트맵)
# ----------------------------------------------------
# 분기별 수익률 계산 (2025Q1, Q2, Q3, Q4, 2026Q1, Q2, Q3)
hyx_q_ret = []
sp_q_ret  = []
q_names   = ['2025 Q1', '2025 Q2', '2025 Q3', '2025 Q4', '2026 Q1', '2026 Q2', '2026 Q3(진행중)']

# 2025 Q1: 1~3월
hyx_q_ret.append((hyx_close['2025-03-31':].iloc[0] if '2025-03-31' in hyx_close else hyx_close['2025-01':'2025-03'].iloc[-1]) / hyx_close['2025-01'].iloc[0] * 100 - 100)
sp_q_ret.append((sp_close['2025-01':'2025-03'].iloc[-1] / sp_close['2025-01'].iloc[0] * 100 - 100))

# 2025 Q2: 4~6월
hyx_q_ret.append((hyx_close['2025-04':'2025-06'].iloc[-1] / hyx_close['2025-01':'2025-03'].iloc[-1] * 100 - 100))
sp_q_ret.append((sp_close['2025-04':'2025-06'].iloc[-1] / sp_close['2025-01':'2025-03'].iloc[-1] * 100 - 100))

# 2025 Q3: 7~9월
hyx_q_ret.append((hyx_close['2025-07':'2025-09'].iloc[-1] / hyx_close['2025-04':'2025-06'].iloc[-1] * 100 - 100))
sp_q_ret.append((sp_close['2025-07':'2025-09'].iloc[-1] / sp_close['2025-04':'2025-06'].iloc[-1] * 100 - 100))

# 2025 Q4: 10~12월
hyx_q_ret.append((hyx_close['2025-10':'2025-12'].iloc[-1] / hyx_close['2025-07':'2025-09'].iloc[-1] * 100 - 100))
sp_q_ret.append((sp_close['2025-10':'2025-12'].iloc[-1] / sp_close['2025-07':'2025-09'].iloc[-1] * 100 - 100))

# 2026 Q1: 1~3월
hyx_q_ret.append((hyx_close['2026-01':'2026-03'].iloc[-1] / hyx_close['2025-10':'2025-12'].iloc[-1] * 100 - 100))
sp_q_ret.append((sp_close['2026-01':'2026-03'].iloc[-1] / sp_close['2025-10':'2025-12'].iloc[-1] * 100 - 100))

# 2026 Q2: 4~6월
hyx_q_ret.append((hyx_close['2026-04':'2026-06'].iloc[-1] / hyx_close['2026-01':'2026-03'].iloc[-1] * 100 - 100))
sp_q_ret.append((sp_close['2026-04':'2026-06'].iloc[-1] / sp_close['2026-01':'2026-03'].iloc[-1] * 100 - 100))

# 2026 Q3: 7~8월 현재
hyx_q_ret.append((hyx_close['2026-07':].iloc[-1] / hyx_close['2026-04':'2026-06'].iloc[-1] * 100 - 100))
sp_q_ret.append((sp_close['2026-07':].iloc[-1] / sp_close['2026-04':'2026-06'].iloc[-1] * 100 - 100))

fig, (ax_bar, ax_heat) = plt.subplots(2, 1, figsize=(14, 11), gridspec_kw={'height_ratios': [1.2, 1]})

x_pos = np.arange(len(q_names))
width = 0.35

rects1 = ax_bar.bar(x_pos - width/2, hyx_q_ret, width, label='SK하이닉스 분기 수익률(%)', color=COLOR_HYX, alpha=0.9)
rects2 = ax_bar.bar(x_pos + width/2, sp_q_ret,  width, label='S&P 500 분기 수익률(%)', color=COLOR_SP, alpha=0.9)

ax_bar.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax_bar.set_title('[분기별 성과] SK하이닉스 vs S&P 500 분기별(Quarterly: 1Q~4Q) 수익률 비교', fontsize=13, fontweight='bold', pad=10)
ax_bar.set_ylabel('분기 수익률 (%)', fontsize=11)
ax_bar.set_xticks(x_pos)
ax_bar.set_xticklabels(q_names, fontsize=10, fontweight='bold')
ax_bar.legend(loc='upper left', fontsize=10)
ax_bar.grid(True, linestyle='--', alpha=0.5, axis='y')

for rect in rects1:
    h = rect.get_height()
    ax_bar.annotate(f'{h:+.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4 if h >= 0 else -14),
                    textcoords="offset points",
                    ha='center', va='bottom' if h >= 0 else 'top', fontsize=9, fontweight='bold', color=COLOR_HYX)

for rect in rects2:
    h = rect.get_height()
    ax_bar.annotate(f'{h:+.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4 if h >= 0 else -14),
                    textcoords="offset points",
                    ha='center', va='bottom' if h >= 0 else 'top', fontsize=9, fontweight='bold', color=COLOR_SP)

# 하단 히트맵 (분기 묶음 표시)
month_labels = ['1월(Q1)','2월(Q1)','3월(Q1)','4월(Q2)','5월(Q2)','6월(Q2)','7월(Q3)','8월(Q3)','9월(Q3)','10월(Q4)','11월(Q4)','12월(Q4)']
hyx_monthly = hyx_ret.resample('ME').sum()

df_m = pd.DataFrame({'year': hyx_monthly.index.year, 'month': hyx_monthly.index.month, 'ret': hyx_monthly.values})
pivot_hyx = df_m.pivot(index='year', columns='month', values='ret')
pivot_hyx.columns = [month_labels[c-1] for c in pivot_hyx.columns]

sns.heatmap(pivot_hyx, ax=ax_heat, cmap='RdYlGn', center=0, annot=True, fmt='+.1f',
            linewidths=1.0, linecolor='#FFFFFF', cbar_kws={'label': '수익률 (%)', 'shrink': 0.8})
ax_heat.set_title('[월별 세부 성과] SK하이닉스 월별 수익률 히트맵 (분기 연계)', fontsize=13, fontweight='bold', pad=10)
ax_heat.set_xlabel('')
ax_heat.set_ylabel('연도', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, '03_monthly_return.png'), dpi=180, bbox_inches='tight')
plt.close()
print("03_monthly_return.png OK")

# ----------------------------------------------------
# 4. 시계열 분해 (STL) - 분기 단위 X축 정렬
# ----------------------------------------------------
stl = STL(hyx_close, period=20, robust=True)
res = stl.fit()

fig, axes = plt.subplots(4, 1, figsize=(14, 11), sharex=True)
data_pairs = [
    (hyx_close,                                      "① 원본 종가 (Raw Data)",         COLOR_HYX),
    (pd.Series(res.trend,    index=hyx_close.index), "② 장기 추세 (Trend Component)",     '#E67E22'),
    (pd.Series(res.seasonal, index=hyx_close.index), "③ 계절성 패턴 (Seasonal Component)", '#2980B9'),
    (pd.Series(res.resid,    index=hyx_close.index), "④ 불규칙 잔차 (Residual / 이벤트 충격)", '#7F8C8D'),
]

for ax, (s, lbl, col) in zip(axes, data_pairs):
    ax.plot(s.index, s.values, color=col, linewidth=1.6)
    ax.set_ylabel(lbl, fontsize=10, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    if "Residual" in lbl:
        ax.axhline(0, color='#333333', linewidth=1.0, linestyle='--')

axes[0].set_title('SK하이닉스 주가 시계열 STL 분해 분석 (분기 주기 기준)', fontsize=14, fontweight='bold', pad=12)
axes[-1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
axes[-1].xaxis.set_major_formatter(plt.FuncFormatter(format_quarter))
axes[-1].set_xlabel('기간 (분기 단위: Q1~Q4)', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, '04_decomposition.png'), dpi=180, bbox_inches='tight')
plt.close()
print("04_decomposition.png OK")
