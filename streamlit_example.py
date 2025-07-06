import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1) 날짜·라벨 --------------------------------------------------------------
periods       = pd.period_range("2024-01", "2025-06", freq="M")
month_keys    = [p.strftime("%Y_%m") for p in periods]
month_labels  = [f"{p.year}년 {p.month}월" for p in periods]
label_to_key  = dict(zip(month_labels, month_keys))

# 2) 주·지표·샘플 데이터 ------------------------------------------------------
us_states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
             "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
             "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
             "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
             "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]

state_names = {  # 50주 + DC
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas",
    "CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware",
    "FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho",
    "IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas",
    "KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
    "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York",
    "NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma",
    "OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina",
    "SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah",
    "VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia",
    "WI":"Wisconsin","WY":"Wyoming","DC":"District of Columbia"
}

metrics = {
    "completion_rate":      "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate":        "광고 클릭율"
}

# 샘플 데이터
np.random.seed(42)
df = pd.DataFrame({"state": us_states})
for m in metrics:
    for mk in month_keys:
        col = f"{m}_{mk}"
        if m == "completion_rate":
            df[col] = np.random.uniform(70, 100, len(us_states))
        elif m == "re_subscription_rate":
            df[col] = np.random.uniform(20, 60, len(us_states))
        else:  # ad_click_rate
            df[col] = np.random.uniform(0.5, 5, len(us_states))  # 0.5% ~ 5%

# 3) 레이아웃 ---------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("미국 주별 KPI 대시보드")
st.session_state.setdefault("selected_metric", "completion_rate")
st.session_state.setdefault("selected_month_label", month_labels[0])

# 4) 지표 선택 ---------------------------------------------------------------
metric_cols = st.columns(3)
for col, (m_key, m_kor) in zip(metric_cols, metrics.items()):
    if col.button(m_kor):
        st.session_state.selected_metric = m_key

# 5) 월 선택 (9×2 그리드) -----------------------------------------------------
st.markdown("#### 월 선택")
rows = [st.columns(9) for _ in range(2)]
for i, lab in enumerate(month_labels):
    r, c = divmod(i, 9)
    with rows[r][c]:
        if st.button(lab, key=f"m_{i}"):
            st.session_state.selected_month_label = lab

selected_month_key = label_to_key[st.session_state.selected_month_label]
metric_kor = metrics[st.session_state.selected_metric]
st.subheader(f"현재 지표: {metric_kor}, 선택 월: {st.session_state.selected_month_label}")

# 6) Choropleth --------------------------------------------------------------
map_col = f"{st.session_state.selected_metric}_{selected_month_key}"
fig = px.choropleth(
    df, locations="state", locationmode="USA-states",
    color=map_col, scope="usa", color_continuous_scale="Blues",
    labels={map_col: metric_kor}, hover_data=["state", map_col],
)
fig.update_layout(margin=dict(r=0,t=0,l=0,b=0),
                  geo=dict(bgcolor='rgba(0,0,0,0)'))

# → 모든 지표에 % 붙이도록 변경
fig.update_layout(coloraxis_colorbar=dict(ticksuffix="%"))

# 7) 주 선택 & 강조 ----------------------------------------------------------
selected_state = st.selectbox(
    "월별 트렌드를 확인할 주를 선택하세요",
    us_states,
    format_func=lambda x: f"{x} ({state_names.get(x,'')})"
)

if selected_state:
    fig.add_trace(
        go.Choropleth(
            locations=[selected_state], locationmode="USA-states",
            z=[0], showscale=False,
            colorscale=[[0,"rgba(0,0,0,0)"],[1,"rgba(0,0,0,0)"]],
            marker_line_color="#c40028",
            marker_line_width=1.5
        )
    )

st.plotly_chart(fig, use_container_width=True)

# 8) 월별 트렌드 -------------------------------------------------------------
if selected_state:
    st.write(f"**선택한 주: {selected_state} ({state_names[selected_state]})**")
    month_cols = [f"{st.session_state.selected_metric}_{mk}" for mk in month_keys]
    vals = df.loc[df["state"] == selected_state, month_cols].values.flatten()
    trend_df = pd.DataFrame({"Month": month_labels, metric_kor: vals})
    trend_fig = px.line(trend_df, x="Month", y=metric_kor, markers=True,
                        title=f"{selected_state} - {metric_kor} 월별 트렌드")
    trend_fig.update_xaxes(categoryorder="array", categoryarray=month_labels)

    # → 모든 지표 y축에 % 붙이기
    trend_fig.update_yaxes(ticksuffix="%")

    st.plotly_chart(trend_fig, use_container_width=True)

# 9) CSS – 버튼 여백 최소화 ---------------------------------------------------
st.markdown("""
<style>
button[kind="primary"]{margin:2px 4px 2px 0 !important;padding:4px 6px !important;}
</style>
""", unsafe_allow_html=True)
