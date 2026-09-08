"""
SK하이닉스 / S&P 500 주가 트렌드 분석 대시보드
─────────────────────────────────────────────
보너스 과제: 분석 결과 서비스화 (대시보드/웹)
실행: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import STL
import os, warnings

warnings.filterwarnings("ignore")

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="SK하이닉스 vs S&P 500 트렌드 분석",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 색상 ─────────────────────────────────────────────────────
C_HYX = "#E65100"
C_SP  = "#1565C0"
C_BG  = "#0E1117"

# ── 데이터 로드 ──────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")


@st.cache_data
def load_data():
    hyx = pd.read_csv(os.path.join(DATA, "skhynix_2025_2026.csv"),
                       index_col=0, parse_dates=True)
    sp  = pd.read_csv(os.path.join(DATA, "sp500_2025_2026.csv"),
                       index_col=0, parse_dates=True)
    if isinstance(hyx.columns, pd.MultiIndex):
        hyx.columns = hyx.columns.get_level_values(0)
    if isinstance(sp.columns, pd.MultiIndex):
        sp.columns = sp.columns.get_level_values(0)
    return hyx, sp


hyx_raw, sp_raw = load_data()

# ── 사이드바 ─────────────────────────────────────────────────
st.sidebar.title("🎛️ 분석 조건 설정")

# 날짜 범위
min_date = max(hyx_raw.index.min(), sp_raw.index.min()).date()
max_date = min(hyx_raw.index.max(), sp_raw.index.max()).date()

date_range = st.sidebar.date_input(
    "📅 분석 기간",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

# 자산 선택
assets = st.sidebar.multiselect(
    "📊 표시할 자산",
    ["SK하이닉스", "S&P 500"],
    default=["SK하이닉스", "S&P 500"],
)

# 이동평균 설정
st.sidebar.markdown("---")
st.sidebar.subheader("📐 이동평균 설정")
ma_short = st.sidebar.slider("단기 이동평균 (일)", 5, 60, 20)
ma_long  = st.sidebar.slider("장기 이동평균 (일)", 20, 120, 60)

# STL 주기
st.sidebar.markdown("---")
st.sidebar.subheader("🔬 STL 분해 설정")
stl_period = st.sidebar.slider("STL period (거래일)", 5, 60, 20)

# ── 데이터 필터링 ────────────────────────────────────────────
hyx = hyx_raw.loc[str(start_d):str(end_d)].copy()
sp  = sp_raw.loc[str(start_d):str(end_d)].copy()

hyx_close = hyx["Close"].dropna()
sp_close  = sp["Close"].dropna()

# ── 헤더 ─────────────────────────────────────────────────────
st.title("📈 SK하이닉스 / S&P 500 주가 트렌드 분석 대시보드")
st.caption("기간·자산·이동평균 일수를 사이드바에서 변경하며 탐색하세요.")

# ── KPI 카드 ─────────────────────────────────────────────────
if len(hyx_close) > 1 and len(sp_close) > 1:
    hyx_ret = (hyx_close.iloc[-1] / hyx_close.iloc[0] - 1) * 100
    sp_ret  = (sp_close.iloc[-1]  / sp_close.iloc[0]  - 1) * 100
    hyx_vol = hyx_close.pct_change().std() * 100
    sp_vol  = sp_close.pct_change().std() * 100
    corr    = hyx_close.pct_change().corr(sp_close.pct_change())

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("SK하이닉스 수익률", f"{hyx_ret:+.1f}%")
    k2.metric("S&P 500 수익률",   f"{sp_ret:+.1f}%")
    k3.metric("SK하이닉스 변동성", f"{hyx_vol:.2f}%")
    k4.metric("S&P 500 변동성",   f"{sp_vol:.2f}%")
    k5.metric("상관계수",          f"{corr:.3f}")

st.markdown("---")

# ── 탭 구성 ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 가격 추이 비교",
    "📉 이동평균 & 크로스",
    "🗓️ 월별 수익률 히트맵",
    "🔬 시계열 분해 (STL)",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — 가격 추이 (정규화 + 이중 축)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    view = st.radio("보기 모드", ["정규화 (100 기준)", "이중 축 (원화 / 포인트)"],
                    horizontal=True)

    if view == "정규화 (100 기준)":
        fig = go.Figure()
        if "SK하이닉스" in assets and len(hyx_close) > 0:
            norm = hyx_close / hyx_close.iloc[0] * 100
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm.values,
                name="SK하이닉스", line=dict(color=C_HYX, width=2)))
        if "S&P 500" in assets and len(sp_close) > 0:
            norm = sp_close / sp_close.iloc[0] * 100
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm.values,
                name="S&P 500", line=dict(color=C_SP, width=2)))
        fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
        fig.update_layout(
            title="정규화 수익률 비교 (시작일 = 100)",
            yaxis_title="정규화 지수",
            xaxis_title="날짜",
            template="plotly_dark", height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # 이중 축
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        if "SK하이닉스" in assets and len(hyx_close) > 0:
            fig.add_trace(go.Scatter(
                x=hyx_close.index, y=hyx_close.values,
                name="SK하이닉스 (원)", line=dict(color=C_HYX, width=2)),
                secondary_y=False)
        if "S&P 500" in assets and len(sp_close) > 0:
            fig.add_trace(go.Scatter(
                x=sp_close.index, y=sp_close.values,
                name="S&P 500 (pt)", line=dict(color=C_SP, width=2)),
                secondary_y=True)
        fig.update_layout(
            title="이중 축 스케일 보정 비교",
            template="plotly_dark", height=500,
        )
        fig.update_yaxes(title_text="SK하이닉스 (원)", secondary_y=False)
        fig.update_yaxes(title_text="S&P 500 (포인트)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — 이동평균 & 골든/데드 크로스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    target = st.radio("분석 대상", ["SK하이닉스", "S&P 500"], horizontal=True)
    close = hyx_close if target == "SK하이닉스" else sp_close
    color = C_HYX if target == "SK하이닉스" else C_SP
    unit  = "원" if target == "SK하이닉스" else "pt"

    if len(close) > ma_long:
        ma_s = close.rolling(ma_short).mean()
        ma_l = close.rolling(ma_long).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=close.index, y=close.values,
            name="종가", line=dict(color="gray", width=1), opacity=0.5))
        fig.add_trace(go.Scatter(
            x=ma_s.index, y=ma_s.values,
            name=f"{ma_short}일 이동평균", line=dict(color=color, width=2.2)))
        fig.add_trace(go.Scatter(
            x=ma_l.index, y=ma_l.values,
            name=f"{ma_long}일 이동평균", line=dict(color="#2E7D32", width=2.2)))

        # 크로스 표시
        golden = (ma_s > ma_l) & (ma_s.shift(1) <= ma_l.shift(1))
        dead   = (ma_s < ma_l) & (ma_s.shift(1) >= ma_l.shift(1))

        for d in close.index[golden]:
            fig.add_vline(x=d, line_dash="dash", line_color="#1565C0",
                          line_width=1.5, opacity=0.7)
        for d in close.index[dead]:
            fig.add_vline(x=d, line_dash="dash", line_color="#C62828",
                          line_width=1.5, opacity=0.7)

        fig.update_layout(
            title=f"{target} — 이동평균 ({ma_short}일 / {ma_long}일) 및 크로스 신호",
            yaxis_title=f"주가 ({unit})",
            template="plotly_dark", height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

        # 크로스 요약 테이블
        gc_dates = [str(d.date()) for d in close.index[golden]]
        dc_dates = [str(d.date()) for d in close.index[dead]]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"🔵 **골든크로스** ({len(gc_dates)}회)")
            st.write(gc_dates if gc_dates else ["없음"])
        with c2:
            st.markdown(f"🔴 **데드크로스** ({len(dc_dates)}회)")
            st.write(dc_dates if dc_dates else ["없음"])
    else:
        st.warning(f"선택한 기간이 {ma_long}일보다 짧아 이동평균을 계산할 수 없습니다.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — 월별 수익률 히트맵
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    target3 = st.radio("분석 대상 ", ["SK하이닉스", "S&P 500"], horizontal=True,
                        key="tab3_target")
    close3 = hyx_close if target3 == "SK하이닉스" else sp_close
    color3 = C_HYX if target3 == "SK하이닉스" else C_SP

    if len(close3) > 20:
        monthly = close3.resample("ME").last().pct_change().dropna() * 100
        df_m = pd.DataFrame({
            "연도": monthly.index.year,
            "월":   monthly.index.month,
            "수익률(%)": monthly.values,
        })
        pivot = df_m.pivot(index="연도", columns="월", values="수익률(%)")
        month_names = {i: f"{i}월" for i in range(1, 13)}
        pivot = pivot.rename(columns=month_names)

        fig = px.imshow(
            pivot,
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            text_auto="+.1f",
            aspect="auto",
            labels=dict(x="월", y="연도", color="수익률(%)"),
        )
        fig.update_layout(
            title=f"{target3} — 월별 수익률 히트맵 (%)",
            template="plotly_dark", height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        # 분기별 바차트
        quarterly = close3.resample("QE").last().pct_change().dropna() * 100
        q_labels = [f"{d.year} Q{(d.month-1)//3+1}" for d in quarterly.index]

        fig_q = go.Figure()
        colors_q = [("#2E7D32" if v >= 0 else "#C62828") for v in quarterly.values]
        fig_q.add_trace(go.Bar(
            x=q_labels, y=quarterly.values,
            marker_color=colors_q,
            text=[f"{v:+.1f}%" for v in quarterly.values],
            textposition="outside",
        ))
        fig_q.update_layout(
            title=f"{target3} — 분기별 수익률",
            yaxis_title="수익률 (%)",
            template="plotly_dark", height=350,
        )
        st.plotly_chart(fig_q, use_container_width=True)
    else:
        st.warning("선택한 기간이 짧아 월별 수익률을 계산할 수 없습니다.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — STL 시계열 분해
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    target4 = st.radio("분석 대상  ", ["SK하이닉스", "S&P 500"], horizontal=True,
                        key="tab4_target")
    close4 = hyx_close if target4 == "SK하이닉스" else sp_close
    color4 = C_HYX if target4 == "SK하이닉스" else C_SP

    if len(close4) > 2 * stl_period:
        stl = STL(close4, period=stl_period, robust=True)
        res = stl.fit()

        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            subplot_titles=["① 원본 종가", "② 장기 추세 (Trend)",
                                            "③ 계절성 (Seasonal)", "④ 잔차 (Residual)"],
                            vertical_spacing=0.06)

        fig.add_trace(go.Scatter(x=close4.index, y=close4.values,
                                  line=dict(color=color4, width=1.5),
                                  showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=close4.index, y=res.trend,
                                  line=dict(color="#E67E22", width=1.5),
                                  showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=close4.index, y=res.seasonal,
                                  line=dict(color="#2980B9", width=1.5),
                                  showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=close4.index, y=res.resid,
                                  line=dict(color="#7F8C8D", width=1.5),
                                  showlegend=False), row=4, col=1)
        fig.add_hline(y=0, row=4, col=1, line_dash="dash",
                      line_color="white", opacity=0.4)

        fig.update_layout(
            title=f"{target4} — STL 시계열 분해 (period={stl_period})",
            template="plotly_dark", height=700,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"💡 사이드바에서 **STL period**를 바꿔보며 추세/계절성 분리 결과가 어떻게 달라지는지 탐색해 보세요.")
    else:
        st.warning(f"선택한 기간이 STL period({stl_period}일)의 2배보다 짧습니다.")

# ── 푸터 ─────────────────────────────────────────────────────
st.markdown("---")
st.caption("데이터 출처: Yahoo Finance (yfinance) | 본 분석은 투자 권유가 아닙니다.")
