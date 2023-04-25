import streamlit as st
from constants import PROBLEMS
from descriptions import PROBLEM_DESCRIPTIONS


def create_problem_overview():

    problem_selection = st.selectbox("Select a problem:", PROBLEMS, index=0)
    problem_selection = problem_selection.lower()

    if problem_selection is not None:
        objectives = PROBLEM_DESCRIPTIONS[problem_selection]["objectives"]
        constraints = PROBLEM_DESCRIPTIONS[problem_selection]["constraints"]

    st.write(f"{problem_selection} has objective(s):")

    for o in objectives:
        st.latex(o)

    st.write(f"Subject to constraint(s):")

    for c in constraints:
        st.latex(c)