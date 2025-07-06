import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go     # ### NEW ###

# ────────────────────────────────────────────────────────────
# 1) 범용 설정 – CSS로 버튼을 ‘다닥다닥’ 붙이기
# ────────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* 월 버튼 여백 최소화 & Treemap‑like 느낌 */
    div.stButton > button {
        margin: 2px 2px 2px 2px;
        padding: 6px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────
# 2) 날짜·지표 기본자료 생성 (2024‑01 ~ 2025‑06, 총 18 개월)
# ────────────────────────────────────────────────────────────
us_states = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

state_names = {           # (생략) – 기존 딕셔너리 그대로
    # ...
}

metrics = {
    "completion_rate": "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate": "광고 클릭율",
}

# 18개월(2024‑01 ~ 2025‑06) 생성
month_range = pd.date_range("2024-01-01", "2025-06-01", freq="MS")
#   화면에 보여줄 한글 라벨
month_display = [f"{d.year}년 {d.month}월" for d in month_range]
#   컬럼명에서 쓸 영문 약어(중복 방지를 위해 ‘Jan‑2024’ 형식)
month_colkey = [d.strftime("%b-%Y") for d in month_range]   # Jan-2024 …

# 난수 기반 가상 데이터
np.random.seed(42)
wide_df = pd.DataFrame({"state": us_states})
for metric_key in metrics.keys():
    for col_id in month_colkey:
        if metric_key == "completion_rate":
            wide_df[f"{metric_key}_{col_id}"] = np.random.uniform(70, 100, len(us_states))
        elif metric_key == "re_subscription_rate":
            wide_df[f"{metric_key}_{col_id}"] = np.random.uniform(20, 60, len(us_states))
        else:
            wide_df[f"{metric_key}_{col_id}"] = np.random.uniform(0.5, 5, len(us_states))

# ────────────────────────────────────────────────────────────
# 3) 세션 스테이트 – 지표 / 월 초기화
# ────────────────────────────────────────────────────────────
if "metric" not in st.session_state:
    st.session_state.metric = "completion_rate"
if "month_idx" not in st.session_state:
    st.session_state.month_idx = 0     # 0 → 2024‑01

# ────────────────────────────────────────────────────────────
# 4) 지표 선택 버튼
# ────────────────────────────────────────────────────────────
st.title("미국 주별 KPI 대시보드")

m1, m2, m3 = st.columns(3)
with m1:
    if st.button("결제 완료율"):
        st.session_state.metric = "completion_rate"
with m2:
    if st.button("재결제율"):
        st.session_state.metric = "re_subscription_rate"
with m3:
    if st.button("광고 클릭율"):
        st.session_state.metric = "ad_click_rate"

# ────────────────────────────────────────────────────────────
# 5) 월 선택 – ‘Treemap‑like’ 버튼 그리드
# ────────────────────────────────────────────────────────────
rows = 3 ; cols = 6                  # 3×6 = 18개
for r in range(rows):
    st_cols = st.columns(cols)
    for c in range(cols):
        idx = r * cols + c
        if idx >= len(month_display): 
            continue
        label = month_display[idx]
        with st_cols[c]:
            if st.button(label):
                st.session_state.month_idx = idx

# 현재 선택 상태
metric_key   = st.session_state.metric
metric_kor   = metrics[metric_key]
month_idx    = st.session_state.month_idx
month_label  = month_display[month_idx]
month_key    = month_colkey[month_idx]          # Jan‑2024 …

st.subheader(f"현재 지표: **{metric_kor}**, 선택 월: **{month_label}**")

# ────────────────────────────────────────────────────────────
# 6) Choropleth – 선택 주 강조하기
# ────────────────────────────────────────────────────────────
map_col = f"{metric_key}_{month_key}"

base_fig = px.choropleth(
    wide_df,
    locations="state",
    locationmode="USA-states",
    color=map_col,
    scope="usa",
    color_continuous_scale="Blues",
    labels={map_col: f"{month_label} {metric_kor}"},
    hover_data={"state": False, map_col: True},
)

# ────────────────────────────────────────────────────────────
# 7) 주 선택(drop‑down) & 해당 주를 지도에서 하이라이트
# ────────────────────────────────────────────────────────────
selected_state = st.selectbox(
    "월별 트렌드를 확인할 주를 선택하세요",
    us_states,
    format_func=lambda x: f"{x} ({state_names[x]})",
    index=us_states.index("CT") if "CT" in us_states else 0,
)

# ‣ 지도 강조용 레이어 (빨간색, 두꺼운 외곽선)
highlight_trace = go.Choropleth(
    locations=[selected_state],          # 선택 주만
    z=[1],                               # dummy 값
    locationmode="USA-states",
    colorscale=[[0, "#ff4d4d"], [1, "#ff4d4d"]],
    showscale=False,
    marker_line_width=3,
    marker_line_color="black",
    hoverinfo="skip",
)

# base → highlight 순으로 trace를 추가
fig = go.Figure(data=base_fig.data + (highlight_trace,))
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    geo=dict(bgcolor="rgba(0,0,0,0)"),
)

st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────
# 8) 선택 주 월별 트렌드 라인차트
# ────────────────────────────────────────────────────────────
monthly_cols = [f"{metric_key}_{k}" for k in month_colkey]
row = wide_df.loc[wide_df.state == selected_state, monthly_cols]

if not row.empty:
    trend_df = pd.DataFrame(
        {"월": month_display, metric_kor: row.values.flatten()}
    )
    trend_fig = px.line(
        trend_df,
        x="월",
        y=metric_kor,
        markers=True,
        title=f"{selected_state} ({state_names[selected_state]}) – {metric_kor} 월별 트렌드",
    )
    trend_fig.update_xaxes(categoryorder="array", categoryarray=month_display)
    st.plotly_chart(trend_fig, use_container_width=True)
else:
    st.warning("해당 주 정보를 찾을 수 없습니다.")
