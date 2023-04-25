import streamlit as st
from constants import PROBLEMS
from descriptions import PROBLEM_DESCRIPTIONS


#def create_problem_overview():
st.title("Problem Overview")
problem_selection = st.selectbox("**Select a Problem:**", PROBLEMS, index=0)
problem_selection = problem_selection.lower()

if problem_selection is not None:
    objectives = PROBLEM_DESCRIPTIONS[problem_selection]["objectives"]
    constraints = PROBLEM_DESCRIPTIONS[problem_selection]["constraints"]

st.write(f"***{problem_selection}*** has Objective(s):")

for o in objectives:
    st.latex(o)

st.write(f"Subject to Constraint(s):")

for c in constraints:
    st.latex(c)