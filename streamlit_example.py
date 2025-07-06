import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --------------------------------------------------
# 1) 날짜·라벨 설정 (2024-01 ~ 2025-06, 총 18개월)
# --------------------------------------------------
periods = pd.period_range(start="2024-01", end="2025-06", freq="M")
month_keys   = [p.strftime("%Y_%m") for p in periods]                 # 내부 컬럼용
month_labels = [f"{p.year}년 {p.month}월" for p in periods]           # 화면 표시용
label_to_key = dict(zip(month_labels, month_keys))

# --------------------------------------------------
# 2) 미국 주/전체 이름, 지표, 샘플 데이터
# --------------------------------------------------
us_states = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

state_names = {
    "AL": "Alabama",        "AK": "Alaska",         "AZ": "Arizona",
    "AR": "Arkansas",       "CA": "California",     "CO": "Colorado",
    "CT": "Connecticut",    "DE": "Delaware",       "FL": "Florida",
    "GA": "Georgia",        "HI": "Hawaii",         "ID": "Idaho",
    "IL": "Illinois",       "IN": "Indiana",        "IA": "Iowa",
    "KS": "Kansas",         "KY": "Kentucky",       "LA": "Louisiana",
    "ME": "Maine",          "MD": "Maryland",       "MA": "Massachusetts",
    "MI": "Michigan",       "MN": "Minnesota",      "MS": "Mississippi",
    "MO": "Missouri",       "MT": "Montana",        "NE": "Nebraska",
    "NV": "Nevada",         "NH": "New Hampshire",  "NJ": "New Jersey",
    "NM": "New Mexico",     "NY": "New York",       "NC": "North Carolina",
    "ND": "North Dakota",   "OH": "Ohio",           "OK": "Oklahoma",
    "OR": "Oregon",         "PA": "Pennsylvania",   "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota",   "TN": "Tennessee",
    "TX": "Texas",          "UT": "Utah",           "VT": "Vermont",
    "VA": "Virginia",       "WA": "Washington",     "WV": "West Virginia",
    "WI": "Wisconsin",      "WY": "Wyoming",        "DC": "District of Columbia"
}

metrics = {
    "completion_rate":      "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate":        "광고 클릭율"
}

# 샘플 데이터 만들기
np.random.seed(42)
df = pd.DataFrame({"state": us_states})
for metric in metrics.keys():
    for mk in month_keys:
        if metric == "completion_rate":
            df[f"{metric}_{mk}"] = np.random.uniform(70, 100, len(us_states))
        elif metric == "re_subscription_rate":
            df[f"{metric}_{mk}"] = np.random.uniform(20, 60, len(us_states))
        else:
            df[f"{metric}_{mk}"] = np.random.uniform(0.5, 5, len(us_states))

# --------------------------------------------------
# 3) 페이지 레이아웃 / 세션 상태
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("미국 주별 KPI 대시보드")

st.session_state.setdefault("selected_metric", "completion_rate")
st.session_state.setdefault("selected_month_label", month_labels[0])

# --------------------------------------------------
# 4) 지표 선택 (버튼 3개)
# --------------------------------------------------
cols = st.columns(3)
for col, (m_key, m_kor) in zip(cols, metrics.items()):
    if col.button(m_kor):
        st.session_state.selected_metric = m_key

# --------------------------------------------------
# 5) 월 선택 (6×3 버튼 그리드)
# --------------------------------------------------
st.markdown("#### 월 선택")
rows = [st.columns(6) for _ in range(3)]           # 18개월 → 3행 6열
for i, label in enumerate(month_labels):
    r, c = divmod(i, 6)
    with rows[r][c]:
        if st.button(label, key=f"m_{i}"):
            st.session_state.selected_month_label = label
selected_month_key = label_to_key[st.session_state.selected_month_label]

metric_kor = metrics[st.session_state.selected_metric]
st.subheader(f"현재 지표: {metric_kor}, 선택 월: {st.session_state.selected_month_label}")

# --------------------------------------------------
# 6) Choropleth 지도 + 선택주 테두리 강조
# --------------------------------------------------
map_col = f"{st.session_state.selected_metric}_{selected_month_key}"
fig = px.choropleth(
    df,
    locations="state",
    locationmode="USA-states",
    color=map_col,
    scope="usa",
    color_continuous_scale="Blues",
    hover_data=["state", map_col],
    labels={map_col: metric_kor},
)
fig.update_layout(margin=dict(r=0, t=0, l=0, b=0),
                  geo=dict(bgcolor='rgba(0,0,0,0)'))

# --------------------------------------------------
# 7) 주 선택 & 월별 트렌드
# --------------------------------------------------
selected_state = st.selectbox(
    "월별 트렌드를 확인할 주를 선택하세요",
    us_states,
    format_func=lambda x: f"{x} ({state_names.get(x, '')})"
)

# 선택한 주를 지도에서 테두리만 굵게 강조
if selected_state:
    fig.add_trace(
        go.Choropleth(
            locations=[selected_state],
            locationmode="USA-states",
            z=[0],  # 투명 처리
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            showscale=False,
            marker_line_color="black",
            marker_line_width=4,
            hoverinfo="skip"
        )
    )

st.plotly_chart(fig, use_container_width=True)

# --- 트렌드 라인 ---
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
            trend_df,
            x="Month", y=metric_kor,
            markers=True,
            title=f"{selected_state} ({state_names.get(selected_state, '')}) - {metric_kor} 월별 트렌드"
        )
        trend_fig.update_xaxes(categoryorder="array", categoryarray=month_labels)
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.warning("해당 주 정보를 찾을 수 없습니다.")

# --------------------------------------------------
# 8) (선택) 버튼 간격/패딩 최소화 CSS
# --------------------------------------------------
st.markdown(
    """
    <style>
    button[kind="primary"] { margin:0 2px 2px 0; padding:4px 6px; }
    .stSlider > div { padding-top: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True
)
