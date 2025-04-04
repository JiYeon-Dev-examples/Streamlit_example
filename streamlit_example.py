import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 미국 주 약어 리스트 (50개 주 + 워싱턴DC)
us_states = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

# 샘플 데이터프레임 생성
# 실제 프로젝트에서는 아래와 같은 형태로 각 지표 값을 불러와 사용해주세요.
np.random.seed(42)  # 재현 가능성을 위해 시드 고정
df = pd.DataFrame({
    'state': us_states,
    'completion_rate': np.random.uniform(70, 100, len(us_states)),  # 예: 결제 완료율(70~100%)
    're_subscription_rate': np.random.uniform(20, 60, len(us_states)),  # 예: 재결제율(20~60%)
    'ad_click_rate': np.random.uniform(0.5, 5, len(us_states))  # 예: 광고 클릭율(0.5~5%)
})

# 페이지 타이틀
st.title("미국 주별 KPI 대시보드")

# 세션 스테이트를 활용해 버튼 클릭 시 지표 전환
if 'metric_index' not in st.session_state:
    st.session_state.metric_index = 0

metrics = ["completion_rate", "re_subscription_rate", "ad_click_rate"]
metric_kor = ["결제 완료율", "재결제율", "광고 클릭율"]

def switch_metric():
    st.session_state.metric_index = (st.session_state.metric_index + 1) % len(metrics)

# 전환 버튼
if st.button("지표 전환"):
    switch_metric()

selected_metric = metrics[st.session_state.metric_index]
selected_metric_kor = metric_kor[st.session_state.metric_index]

# 현재 지표 표시
st.subheader(f"현재 지표: {selected_metric_kor}")

# Choropleth 그리기
# locationmode="USA-states", scope="usa"를 사용해야 미국 지도에 제대로 표시됩니다.
fig = px.choropleth(
    df,
    locations='state',
    locationmode="USA-states",
    color=selected_metric,
    scope="usa",
    color_continuous_scale="Blues",
    labels={selected_metric: selected_metric_kor},
    hover_data=['state', selected_metric]
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    geo=dict(bgcolor='rgba(0,0,0,0)')
)

st.plotly_chart(fig, use_container_width=True)
