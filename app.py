import streamlit as st
from descriptions import PROBLEM_DESCRIPTIONS
import screens
from constants import SCREENS

st.set_page_config(layout="wide")

screen_selection = st.sidebar.selectbox("Select a screen:", SCREENS, index=0)
screens.display_screen(screen_selection)