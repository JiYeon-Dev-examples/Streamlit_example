import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 페이지 레이아웃 설정
st.set_page_config(layout="wide")

# 타이틀
st.title("예시 대시보드: 결제 완료율, 재결제율, 광고 클릭율")
st.markdown("2025년 1월부터 12월까지의 임의 데이터로 작성한 대시보드 예시입니다.")

# ------------------------------------
# 1) 월별 임의 데이터 생성
# ------------------------------------
months = pd.date_range(start='2025-01-01', periods=12, freq='MS')

np.random.seed(42)  # 예시 재현성(선택)
df = pd.DataFrame({
    'Month': months,
    # 결제 완료율을 평균 44% 근처로: 42% ~ 46% 사이
    '결제 완료율': np.random.uniform(0.42, 0.46, 12),
    # 재결제율: 15% ~ 30% 사이
    '재결제율': np.random.uniform(0.15, 0.30, 12),
    # 광고 클릭율: 5% ~ 15% 사이
    '광고 클릭율': np.random.uniform(0.05, 0.15, 12)
})

# 월(YYYY-MM) 텍스트 컬럼 추가
df['Month_str'] = df['Month'].dt.strftime('%Y-%m')

# ------------------------------------
# 2) 메트릭(지표 카드) 섹션
# ------------------------------------
# 최신(12월) 데이터만 따로 뽑아 지표 표시
last_row = df.iloc[-1]
col1, col2, col3 = st.columns(3)

col1.metric(
    label="결제 완료율 (12월)",
    value=f"{last_row['결제 완료율']:.2%}"
)
col2.metric(
    label="재결제율 (12월)",
    value=f"{last_row['재결제율']:.2%}"
)
col3.metric(
    label="광고 클릭율 (12월)",
    value=f"{last_row['광고 클릭율']:.2%}"
)

# ------------------------------------
# 3) 전체 추이 (꺾은선 그래프)
# ------------------------------------
st.subheader("월별 지표 추이")

# Altair를 사용해 세 지표를 한 번에 꺾은선 그래프로 표시
melted_df = df.melt(
    id_vars='Month_str',
    value_vars=['결제 완료율', '재결제율', '광고 클릭율'],
    var_name='지표',
    value_name='값'
)

chart = (
    alt.Chart(melted_df)
    .mark_line(point=True)
    .encode(
        x=alt.X('Month_str:N', title='월'),
        y=alt.Y('값:Q', title='비율'),
        color=alt.Color('지표:N', scale=alt.Scale(
            domain=["결제 완료율", "재결제율", "광고 클릭율"],
            range=["#205781", "#4F959D", "#98D2C0"]
        )),
        tooltip=['Month_str', '지표', alt.Tooltip('값:Q', format='.2%')]
    )
    .properties(width=800, height=400)
)

st.altair_chart(chart, use_container_width=True)

# ------------------------------------
# 4) 데이터프레임 미리보기
# ------------------------------------
st.subheader("데이터프레임 미리보기")
st.dataframe(df.drop(columns='Month'), use_container_width=True)
