import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------
# 1) 날짜·라벨 설정
# ---------------------------------------
periods = pd.period_range(start="2024-01", end="2025-06", freq="M")
month_keys   = [p.strftime("%Y_%m") for p in periods]             # 내부 컬럼 식별자
month_labels = [f"{p.year}년 {p.month}월" for p in periods]       # 화면용 라벨
label_to_key = dict(zip(month_labels, month_keys))

# 미국 50개 주 + DC
us_states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
             "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
             "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
             "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
             "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]

state_names = {           # …중략 (기존 딕셔너리 그대로) ...
    "WY": "Wyoming"
}

metrics = {
    "completion_rate": "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate": "광고 클릭율"
}

# ---------------------------------------
# 2) 가상 데이터 생성
# ---------------------------------------
np.random.seed(42)
df = pd.DataFrame({"state": us_states})
for metric in metrics.keys():
    for mk in month_keys:
        if metric == "completion_rate":
            df[f"{metric}_{mk}"] = np.random.uniform(70, 100, len(us_states))
        elif metric == "re_subscription_rate":
            df[f"{metric}_{mk}"] = np.random.uniform(20, 60, len(us_states))
        else:  # ad_click_rate
            df[f"{metric}_{mk}"] = np.random.uniform(0.5, 5, len(us_states))

# ---------------------------------------
# 3) 페이지 레이아웃
# ---------------------------------------
st.title("미국 주별 KPI 대시보드")

# 세션 상태 기본값
st.session_state.setdefault("selected_metric", "completion_rate")
st.session_state.setdefault("selected_month_label", month_labels[0])

# --- 지표 선택 (버튼 3개) ---
cols = st.columns(3)
for col, (m_key, m_kor) in zip(cols, metrics.items()):
    if col.button(m_kor):
        st.session_state.selected_metric = m_key

# --- 월 선택 (select_slider = 다닥다닥 붙는 슬라이더) ---
st.markdown("#### 월 선택")
st.session_state.selected_month_label = st.select_slider(
    " ",
    options=month_labels,
    value=st.session_state.selected_month_label,
    label_visibility="collapsed",
)
selected_month_key = label_to_key[st.session_state.selected_month_label]

# 현재 선택 상태 표시
metric_kor = metrics[st.session_state.selected_metric]
st.subheader(f"현재 지표: {metric_kor}, 선택 월: {st.session_state.selected_month_label}")

# ---------------------------------------
# 4) Choropleth 지도
# ---------------------------------------
map_col = f"{st.session_state.selected_metric}_{selected_month_key}"
fig = px.choropleth(
    df,
    locations="state",
    locationmode="USA-states",
    color=map_col,
    scope="usa",
    color_continuous_scale="Blues",
    labels={map_col: metric_kor},
    hover_data=["state", map_col],
)
fig.update_layout(
    margin=dict(r=0, t=0, l=0, b=0),
    geo=dict(bgcolor='rgba(0,0,0,0)')
)

# ---------------------------------------
# 5) 주 선택 & 트렌드 라인
# ---------------------------------------
selected_state = st.selectbox(
    "월별 트렌드를 확인할 주를 선택하세요",
    us_states,
    format_func=lambda x: f"{x} ({state_names.get(x, '')})"
)

# --- 지도에서 해당 주 강조(빨간 점) ---
if selected_state:
    fig.add_trace(
        go.Scattergeo(
            locations=[selected_state],
            locationmode="USA-states",
            marker=dict(size=14, color="red", line=dict(color="black", width=2)),
            showlegend=False,
            hoverinfo="skip",
        )
    )

st.plotly_chart(fig, use_container_width=True)

# --- 월별 트렌드 라인 ---
if selected_state:
    st.write(f"**선택한 주: {selected_state} ({state_names.get(selected_state, '')})**")
    month_cols = [f"{st.session_state.selected_metric}_{mk}" for mk in month_keys]
    row = df.loc[df["state"] == selected_state, month_cols]
    if not row.empty:
        trend_df = pd.DataFrame({
            "Month": month_labels,
            metric_kor: row.values.flatten()
        })
        trend_fig = px.line(
            trend_df, x="Month", y=metric_kor, markers=True,
            title=f"{selected_state} ({state_names.get(selected_state, '')}) - {metric_kor} 월별 트렌드"
        )
        trend_fig.update_xaxes(categoryorder="array", categoryarray=month_labels)
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.warning("해당 주 정보를 찾을 수 없습니다.")

# ---------------------------------------
# 6) (선택) CSS 미세 조정
# ---------------------------------------
st.markdown(
    """
    <style>
    /* 슬라이더 레이블 글꼴/패딩 조정 */
    .stSlider > div { padding-top: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True
)
