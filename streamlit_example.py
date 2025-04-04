import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# ---------------------------------------
# 1) 데이터 준비
# ---------------------------------------
# 미국 주 약어 리스트 (50개 주 + 워싱턴DC)
us_states = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

# 미국 주 전체 이름 매핑
state_names = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

# 지표별 한글 라벨 매핑
metrics = {
    "completion_rate": "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate": "광고 클릭율"
}

# 1~12월(영문 축약)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 가상 데이터프레임 생성 (각 지표별 12개월 데이터)
np.random.seed(42)
df = pd.DataFrame({"state": us_states})
for metric_key in metrics.keys():
    for month in months:
        col_name = f"{metric_key}_{month}"
        if metric_key == "completion_rate":
            df[col_name] = np.random.uniform(70, 100, len(us_states))
        elif metric_key == "re_subscription_rate":
            df[col_name] = np.random.uniform(20, 60, len(us_states))
        else:  # ad_click_rate
            df[col_name] = np.random.uniform(0.5, 5, len(us_states))

# ---------------------------------------
# 2) 페이지 레이아웃 및 초기 상태
# ---------------------------------------
st.title("미국 주별 KPI 대시보드")

# 세션 스테이트에 현재 선택된 지표와 월을 저장
if "selected_metric" not in st.session_state:
    st.session_state.selected_metric = "completion_rate"
if "selected_month" not in st.session_state:
    st.session_state.selected_month = "Jan"

# ---------------------------------------
# 3) 지표 선택 버튼들
# ---------------------------------------
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

# ---------------------------------------
# 4) 월별 선택 버튼들 (1~12월)
# ---------------------------------------
# 버튼이 많으므로 두 줄로 나누어 배치합니다.
month_cols_1 = st.columns(6)
month_cols_2 = st.columns(6)
for i, m in enumerate(months[:6]):
    with month_cols_1[i]:
        if st.button(m):
            st.session_state.selected_month = m
for i, m in enumerate(months[6:]):
    with month_cols_2[i]:
        if st.button(m):
            st.session_state.selected_month = m

# 현재 선택된 지표와 월 표시
selected_metric = st.session_state.selected_metric
selected_month = st.session_state.selected_month
selected_metric_kor = metrics[selected_metric]
st.subheader(f"현재 지표: {selected_metric_kor}, 선택 월: {selected_month}")

# ---------------------------------------
# 5) Choropleth 지도 생성
# ---------------------------------------
# 선택된 지표와 월에 해당하는 컬럼 지정
map_col = f"{selected_metric}_{selected_month}"
fig = px.choropleth(
    df,
    locations="state",
    locationmode="USA-states",
    color=map_col,
    scope="usa",
    color_continuous_scale="Blues",
    labels={map_col: f"{selected_month} {selected_metric_kor}"},
    hover_data=["state", map_col]
)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    geo=dict(bgcolor='rgba(0,0,0,0)')
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------
# 6) 주 선택 드롭다운 및 월별 트렌드 그래프
# ---------------------------------------
# selectbox의 format_func를 이용해 "약어 (전체이름)" 형태로 표시
selected_state = st.selectbox(
    "월별 트렌드를 확인할 주를 선택하세요",
    us_states,
    format_func=lambda x: f"{x} ({state_names.get(x, '')})"
)
if selected_state:
    st.write(f"**선택한 주: {selected_state} ({state_names.get(selected_state, '')})**")
    # 선택된 지표에 대해 1월~12월 컬럼명 생성
    monthly_cols = [f"{selected_metric}_{m}" for m in months]
    state_row = df.loc[df["state"] == selected_state, monthly_cols]
    if not state_row.empty:
        monthly_values = state_row.values.flatten()
        trend_df = pd.DataFrame({
            "Month": months,
            selected_metric_kor: monthly_values
        })
        trend_fig = px.line(
            trend_df,
            x="Month",
            y=selected_metric_kor,
            markers=True,
            title=f"{selected_state} ({state_names.get(selected_state, '')}) - {selected_metric_kor} 월별 트렌드"
        )
        trend_fig.update_xaxes(categoryorder='array', categoryarray=months)
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.warning("해당 주 정보를 찾을 수 없습니다.")
