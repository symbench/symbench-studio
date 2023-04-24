import streamlit as st


from driver import call_solver
from descriptions import PROBLEM_DESCRIPTIONS

st.set_page_config(
    layout="wide"
)

PROBLEMS = ["BNH", "OSY", "TNK"]
SOLVERS = ["pymoo", "constraint_prog", "compare solutions"]

st.write("Welcome to Symbench Studio")
problem_selection = st.selectbox("Select a problem:", PROBLEMS, index=0)
problem_selection = problem_selection.lower()
solver_selection = st.selectbox("Select a solver:", SOLVERS, index=0)
visualize_results = st.checkbox("Visualize results?")

if problem_selection is not None:
    objectives = PROBLEM_DESCRIPTIONS[problem_selection]["objectives"]
    constraints = PROBLEM_DESCRIPTIONS[problem_selection]["constraints"]

st.write(f"{problem_selection} has objective(s):")

for o in objectives:
    st.latex(o)

st.write(f"Subject to constraint(s):")

for c in constraints:
    st.latex(c)

st.write("tunable parameters:")

solve_button = st.button("Solve")

if solve_button:

    print(f"calling {problem_selection} with {solver_selection}")

    # loading screen while the solver is running
    with st.spinner("Solving..."):
        call_solver(problem_selection, solver_selection)

    if visualize_results:
        st.write("visualize results")