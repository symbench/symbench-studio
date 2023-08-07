import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from constants import DEFAULT_RESULTS_ABSPATH

def load_data():
    csv_path = "/Users/michael/Github/symbench-studio/symbench-dataset/symbench_dataset/results/pymoo/result_bnh/test_hist.csv"
    return pd.read_csv(csv_path)

def get_result_fig(cols=None):
    df = st.session_state.dfs[st.session_state.dfs['iter'] <= st.session_state['slider_value']]
    
    fig = go.Figure()
    trace = go.Scatter(x=df['p1'], 
                       y=df['p2'],
                       mode='markers',
                       visible=True,
                       name=f"num sols={len(df)}",
            )
    fig.add_trace(trace)
    fig.update_layout(
        title=f"Test Plot for {st.session_state['slider_value']}",
        xaxis_title='p1',
        yaxis_title='p2',
        margin=dict(l=50, r=50, t=50, b=50),
    )
    return fig

# Load data if not already loaded
if 'dfs' not in st.session_state:
    st.session_state.dfs = load_data()

# Default slider value
if "slider_value" not in st.session_state:
    st.session_state["slider_value"] = 10

st.header("Nested Widgets")

# Slider
slider_value = st.slider("Select a range of values", 1, 20, st.session_state['slider_value'])
if slider_value != st.session_state['slider_value']: # Only update if value changed to prevent unnecessary reruns
    st.session_state['slider_value'] = slider_value

# Display plot
fig = get_result_fig()
st.plotly_chart(fig, use_container_width=True)
