import streamlit as st
from plots import plot_pareto_front

#def create_data_view():
st.title("Pareto Front and Metrics")
p = plot_pareto_front()
st.plotly_chart(p, use_container_width=True)