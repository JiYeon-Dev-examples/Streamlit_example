import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# (중요) 지도 클릭 이벤트 처리를 위해 별도 라이브러리 사용
# pip install streamlit-plotly-events
from streamlit_plotly_events import plotly_events

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

# 지표별 한글 라벨 매핑
metrics = {
    "completion_rate": "결제 완료율",
    "re_subscription_rate": "재결제율",
    "ad_click_rate": "광고 클릭율"
}

# 1~12월(영문 축약)
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# 가상 데이터프레임 생성
# 지표 3종 x 12개월 분량의 데이터를 state별로 가지는 형태
np.random.seed(42)  # 재현 가능성 유지
df = pd.DataFrame({"state": us_states})

# 각 지표별 월별 컬럼 생성, 예: completion_rate_Jan ~ completion_rate_Dec
for metric_key in metrics.keys():
    for month in months:
        col_name = f"{metric_key}_{month}"
        if metric_key == "completion_rate":
            df[col_name] = np.random.uniform(70, 100, len(us_states))   # 예) 70~100%
        elif metric_key == "re_subscription_rate":
            df[col_name] = np.random.uniform(20, 60, len(us_states))    # 예) 20~60%
        else:  # ad_click_rate
            df[col_name] = np.random.uniform(0.5, 5, len(us_states))    # 예) 0.5~5%

# ---------------------------------------
# 2) 페이지 레이아웃 및 초기 상태
# ---------------------------------------
st.title("미국 주별 KPI 대시보드")

# 세션 스테이트에서 현재 선택된 지표, 월 관리
if "selected_metric" not in st.session_state:
    st.session_state.selected_metric = "completion_rate"
if "selected_month" not in st.session_state:
    st.session_state.selected_month = "Jan"

# ---------------------------------------
# 3) 지표 선택 버튼들
# ---------------------------------------
metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    if st.button("결제 완료율"):
        st.session_state.selected_metric = "completion_rate"
with metric_col2:
    if st.button("재결제율"):
        st.session_state.selected_metric = "re_subscription_rate"
with metric_col3:
    if st.button("광고 클릭율"):
        st.session_state.selected_metric = "ad_click_rate"

# ---------------------------------------
# 4) 월별 선택 버튼들 (1~12월)
# ---------------------------------------
# 너무 많은 버튼이 한 줄에 들어가면 UI가 깨질 수 있으니
# 예시로 6개씩 나눠서 2줄에 배치합니다. (원하시는 대로 조정 가능)
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

# 현재 선택된 지표, 월
selected_metric = st.session_state.selected_metric
selected_month = st.session_state.selected_month
selected_metric_kor = metrics[selected_metric]

st.subheader(f"현재 지표: {selected_metric_kor}, 선택 월: {selected_month}")

# ---------------------------------------
# 5) 지도 (Choropleth) 생성
# ---------------------------------------
# - 지도 색상은 선택된 지표의 해당 월 컬럼 사용
map_col = f"{selected_metric}_{selected_month}"

fig = px.choropleth(
    df,
    locations="state",
    locationmode="USA-states",
    color=map_col,
    scope="usa",
    color_continuous_scale="Blues",
    labels={map_col: f"{selected_month} {selected_metric_kor}"},
    hover_data=["state", map_col],
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    geo=dict(bgcolor='rgba(0,0,0,0)')
)

# ---------------------------------------
# 6) 지도 클릭 이벤트 처리 -> 월별 트렌드 그래프
# ---------------------------------------
# - plotly_events로 지도 클릭 시, 클릭된 주 정보(location) 얻기
# - 참고: https://pypi.org/project/streamlit-plotly-events/
clicked_points = plotly_events(
    fig,
    click_event=True,     # 클릭 이벤트만 수신
    hover_event=False,
    select_event=False,
    override_height=600,  # 지도 높이 조절
    override_width="100%",# 지도 너비 조절
)

# 만약 사용자가 지도 상에서 주를 클릭했다면
if clicked_points:
    # plotly_events가 반환하는 정보 중, 'location'에 주 약어가 들어 있음
    clicked_state = clicked_points[0].get("location", None)

    if clicked_state:
        st.write(f"**선택한 주: {clicked_state}**")

        # 해당 주의 월별 데이터 (해당 metric만) 추출
        # 예) [completion_rate_Jan, completion_rate_Feb, ..., completion_rate_Dec] 값
        monthly_cols = [f"{selected_metric}_{m}" for m in months]
        state_row = df.loc[df["state"] == clicked_state, monthly_cols]

        if not state_row.empty:
            # state_row는 DataFrame 형태이므로 값만 추출
            monthly_values = state_row.values.flatten()  # 1D array

            # 트렌드용 임시 DF 생성
            trend_df = pd.DataFrame({
                "Month": months,
                selected_metric_kor: monthly_values
            })

            # 라인 차트
            trend_fig = px.line(
                trend_df,
                x="Month",
                y=selected_metric_kor,
                markers=True,  # 각 점 표시
                title=f"{clicked_state} - {selected_metric_kor} 월별 트렌드"
            )
            # x축 순서를 Jan ~ Dec로 강제 정렬 (문자열이므로 직접 순서 지정)
            trend_fig.update_xaxes(categoryorder='array', categoryarray=months)

            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.warning("해당 주 정보를 찾을 수 없습니다.")
else:
    st.info("지도를 클릭하면 해당 주의 월별 트렌드를 확인할 수 있습니다.")
