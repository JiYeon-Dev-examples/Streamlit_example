import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------
# 1) 기본 데이터 준비
# ---------------------------------------
# 미국 주 약어 리스트 (50개 주 + 워싱턴DC)
us_states = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

# 샘플 기본 지표 컬럼 (연간 혹은 대표값)
np.random.seed(42)  # 재현 가능성을 위해 시드 고정
df = pd.DataFrame({
    'state': us_states,
    'completion_rate': np.random.uniform(70, 100, len(us_states)),      # 예: 결제 완료율(70~100%)
    're_subscription_rate': np.random.uniform(20, 60, len(us_states)),  # 예: 재결제율(20~60%)
    'ad_click_rate': np.random.uniform(0.5, 5, len(us_states))          # 예: 광고 클릭율(0.5~5%)
})

# ---------------------------------------
# 2) 2025년 1~12월 월별 데이터 추가
# ---------------------------------------
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 각 지표별로 12개월 컬럼 생성 (예: completion_rate_Jan ~ completion_rate_Dec)
for metric in ["completion_rate", "re_subscription_rate", "ad_click_rate"]:
    for month in months:
        # 예시: "completion_rate_Jan" 형태의 컬럼명
        col_name = f"{metric}_{month}"
        # 가상 데이터 생성: 각 주마다 난수
        if metric == "completion_rate":
            # 대략 70~100% 범위에서 월별 변동
            df[col_name] = np.random.uniform(70, 100, len(us_states))
        elif metric == "re_subscription_rate":
            # 대략 20~60% 범위에서 월별 변동
            df[col_name] = np.random.uniform(20, 60, len(us_states))
        else:  # ad_click_rate
            # 대략 0.5~5% 범위에서 월별 변동
            df[col_name] = np.random.uniform(0.5, 5, len(us_states))

# ---------------------------------------
# 3) Streamlit 앱 구성
# ---------------------------------------
st.title("미국 주별 KPI 대시보드 (월별 트렌드 포함)")

# 지표별 한글 라벨 매핑
metrics = {
    "completion_rate": "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate": "광고 클릭율"
}

# 세션 스테이트에서 현재 선택된 지표 관리
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = 'completion_rate'

# 개별 버튼을 통해 지표 전환
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

selected_metric = st.session_state.selected_metric
selected_metric_kor = metrics[selected_metric]

# 현재 지표 표시
st.subheader(f"현재 지표: {selected_metric_kor}")

# ---------------------------------------
# 4) Choropleth 및 hover_data 설정
# ---------------------------------------
# 4-1) 지표와 월별 데이터 컬럼명 만들기
#      예: completion_rate, completion_rate_Jan, ..., completion_rate_Dec
monthly_columns = [f"{selected_metric}_{m}" for m in months]  # 예: completion_rate_Jan ~ Dec

# 4-2) hover_data에 선택된 지표의 월별 컬럼까지 포함
#      -> 지도에서 각 주에 마우스 호버 시 월별 정보가 툴팁에 표시됨
hover_data_cols = ["state", selected_metric] + monthly_columns

# Choropleth 생성
fig = px.choropleth(
    df,
    locations='state',
    locationmode="USA-states",
    color=selected_metric,
    scope="usa",
    color_continuous_scale="Blues",
    labels={selected_metric: selected_metric_kor},
    hover_data=hover_data_cols  # 핵심: 월별 컬럼도 툴팁에 포함
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    geo=dict(bgcolor='rgba(0,0,0,0)')
)

st.plotly_chart(fig, use_container_width=True)
