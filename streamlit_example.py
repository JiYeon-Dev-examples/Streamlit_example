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

# 지표별 영문 키와 한글 라벨을 dict로 매핑
metrics = {
    "completion_rate": "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate": "광고 클릭율"
}

# 세션 스테이트에서 현재 선택된 지표 관리
# 기본값으로 "completion_rate" 세팅
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = 'completion_rate'

# 개별 버튼 클릭 시 해당 지표로 전환
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("결제 완료율"):
        st.session_state.selected_metric = "completion_rate"
with col2:
    if st.button("재결제율"):
        st.session_state.selected_metric = "re_subscription_rate"
with col3:
    if st.button("광고 클릭율"):
        st.session_state.selected_metric = "ad_click_rate"

# 현재 선택된 지표와 한글 라벨
selected_metric = st.session_state.selected_metric
selected_metric_kor = metrics[selected_metric]

# 현재 지표 표시
st.subheader(f"현재 지표: {selected_metric_kor}")

# Choropleth 그리기
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
