import streamlit as st
import os 
from constants import PROBLEMS_ABSPATH, RESULTS_ABSPATH, PROBLEM_SPECS_ABSPATH
import subprocess

def problem_selection():
    available_problems = os.listdir(PROBLEMS_ABSPATH)
    selected_problem = st.selectbox("Select an optimization problem", available_problems, index=0)
    st.write(f"Input summary for {selected_problem}:")
    selected_problem_path = os.path.join(PROBLEMS_ABSPATH, selected_problem)
    
    import re
    with open(os.path.join(selected_problem_path, 'input.txt'), 'r') as f:
        contents = f.read()

    # Parse variables, constraints, and projections using regular expressions
    num_variables = len(re.findall(r'^variable', contents, re.MULTILINE))
    num_constraints = len(re.findall(r'^constraint', contents, re.MULTILINE))
    num_projections = len(re.findall(r'^projection', contents, re.MULTILINE))

    # Parse objective function using regular expressions
    objective = re.search(r'(maximize|minimize)\s+[a-zA-Z0-9_]+\s*$', contents, re.MULTILINE)
    if objective:
        objective = objective.group(1)

        st.write("Number of variables: ", num_variables)
        st.write("Number of constraints: ", num_constraints)
        st.write("Number of projections: ", num_projections)
        if objective:
            st.write(f'Optimization objective: {objective}')
        else:
            st.write('Optimization objective not found')

    problem_info = subprocess.run(["symbench-dataset", "info", "--print_problem", selected_problem], capture_output=True, text=True)
    print(f" problem_info: {problem_info.stdout}")
    st.write(problem_info.stdout)

    # select a solver: pymoo, constraint_prog, z3, GA_simple, scipy
    selected_solver = st.selectbox("Select a solver:", ["", "pymoo", "constraint_prog", "z3", "GA_simple", "scipy"], index=0)

    if selected_solver:
        solve_button_press = st.button("Solve")
        if solve_button_press:
            #st.write("solve button press")

            # call symbench-dataset solve selected_problem with subprocess
            with st.spinner("Solving..."):
                solve_process = subprocess.run(["symbench-dataset", "solve", "--problem", selected_problem, "--solver", selected_solver])
            #st.write("Results saved to ")

def problem_generation(selected_problems):

    for problem in selected_problems:
        dirpath = os.path.join(PROBLEM_SPECS_ABSPATH, problem)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        filepath = os.path.join(dirpath, 'input.txt')
        subprocess.run(["cp-problems-generator", "dump", "--output-file", filepath, problem])
    