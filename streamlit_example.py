import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_plotly_events import plotly_events

us_states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
             "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
             "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
             "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
             "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]

df = pd.DataFrame({
    "state": us_states,
    "completion_rate_Jan": np.random.uniform(0, 100, len(us_states))
})

st.title("테스트 대시보드")

fig = px.choropleth(
    df,
    locations="state",
    locationmode="USA-states",
    color="completion_rate_Jan",
    scope="usa",
    color_continuous_scale="Blues",
    hover_data=["state", "completion_rate_Jan"],
)

st.plotly_chart(fig, use_container_width=True)

clicked_points = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    override_height=600,
    override_width="100%",
)

st.write("Clicked Points:", clicked_points)
