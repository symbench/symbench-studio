import streamlit as st
import os
import shutil
from constants import PROBLEMS, SOLVERS, DEFAULT_RESULTS_ABSPATH, USER_RESULTS_ABSPATH, DEFAULT_PROBLEM_INPUTS_ABSPATH, USER_PROBLEM_INPUTS_ABSPATH

import re
import subprocess
import sys
import time
import pandas as pd
import plotly.express as px
import uuid


def solve_problem(num_generations=None, num_points=None, num_iters=None):

    solve_cmd = f"symbench-dataset solve --problem {st.session_state.problem_name} --solver {st.session_state.solver_name}"

    if st.session_state.solver_name == "pymoo" and num_generations is not None:
        solve_cmd = solve_cmd + f" --ngen {num_generations}"
    elif st.session_state.solver_name == "constraint_prog" and num_points is not None and num_iters is not None:
        solve_cmd = solve_cmd + f" --num_points {num_points} --num_iters {num_iters}"
    
    problem_input_path = DEFAULT_PROBLEM_INPUTS_ABSPATH

    if st.session_state.from_user:
        input_file_path = os.path.join(USER_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, "input.txt")
        solve_cmd += " --user"
        problem_input_path = USER_PROBLEM_INPUTS_ABSPATH

    input_file_path = os.path.join(problem_input_path, st.session_state.problem_name, "input.txt")
    
    print(f"solving problem with input file {input_file_path} using solver {st.session_state.solver_name}")
    print(f" ==== running command {solve_cmd.split(' ')}")
    #st.write(f" ==== running command {solve_cmd}")
    process = subprocess.Popen(solve_cmd.split(" "), stdout=subprocess.PIPE)

    result_csv_path = os.path.join(st.session_state.base_save_path, st.session_state.solver_name, f"result_{st.session_state.problem_name}.csv")
    st.session_state.result_csv_path = result_csv_path
    print(f"result csv path is: {result_csv_path}")

    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            yield output.decode("utf-8")

    rc = process.poll()

    # if rc is not None:
    #     while not os.path.exists(result_csv_path):
    #         time.sleep(0.1)

    #print(f"result csv path is: {result_csv_path}")
    #assert os.path.exists(result_csv_path), f"result csv path {result_csv_path} does not exist"
    
    return rc


   # if os.path.exists(result_csv_path):
        #solution_container = st.container()
        #result_df = pd.read_csv(result_csv_path)
        #st.write(result_df)

    

def load_input_file():

    problem_name = st.session_state.problem_name
    if "_user" in problem_name:
        problem_name = problem_name.replace("_user", "")
    if st.session_state.from_user:
        file_path = os.path.join(USER_PROBLEM_INPUTS_ABSPATH, problem_name, "input.txt")
    else:
        file_path = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, problem_name, "input.txt")
    print(f"loading default input file at: {file_path}")
    with open(file_path, "r") as f:
        content = f.read()
    print(content)
    st.session_state.input_text_area = content


def save_user_modified_input_file(content):
    if "_user" in st.session_state.problem_name:
        problem_name = st.session_state.problem_name.replace("_user", "")
    file_path = os.path.join(USER_PROBLEM_INPUTS_ABSPATH, problem_name, "input.txt")
    
    # remove empty lines for parser
    #content = [line for line in content if line.strip() != ""]

    print(f"content is: {content}")

    print(f"saving user modified input file at {file_path}")
    with open(file_path, "w") as f:
        f.write(content)
    st.session_state.from_user = True


def on_text_area_change():
    print("saving changes")
    content = st.session_state[st.session_state.input_text_area_key]
    if content != st.session_state.previous_input_text_area:
        result = validate_user_input(content)
        if result is True:
            problem_description_container.success("Valid input file")
            print(f"saving content: {st.session_state.input_text_area}")
            save_user_modified_input_file(content)
            st.session_state.from_user = True
            st.session_state.base_save_path = USER_RESULTS_ABSPATH
            problem_description_container.write("Saved user modified file")
        st.session_state.previous_input_text_area = content


def validate_user_input(content):
    print("validating user input")

    # allow empty lines
    input_str = [line for line in content.strip().split("\n") if line != ""]

    line_number = 1
    
    variable_pattern = re.compile(r'^variable\s+\w+\s+-?\d+(\.\d+)?\s+-?\d+(\.\d+)?$')
    #constraint_pattern = re.compile(r'^constraint\s+\w+\s+(leq|geq)\(.+\,-?\d+(\.\d+)?\)$')
    constraint_pattern = re.compile(r'^constraint\s+\w+\s+(leq|geq)\(.+?\)$')
    projection_pattern = re.compile(r'^projection\s+\w+\s+.+$')
    optimize_pattern = re.compile(r'^(minimize|maximize)\s+\w+$')

    line_formats = set()

    for line in input_str:
        # Ignore comment lines
        if line.strip().startswith('#'):
            continue
        
        if variable_pattern.match(line):
            line_formats.add('variable')
        elif constraint_pattern.match(line):
            line_formats.add('constraint')
        elif projection_pattern.match(line):
            line_formats.add('projection')
        elif optimize_pattern.match(line):
            line_formats.add('optimize')
        else:
            problem_description_container.error(f"Invalid format at line {line_number}: {line}")
            return False
        
        line_number += 1

    # # If line formats change, return an error
    # if len(line_formats) > 4: # You have 4 expected line formats
    #     st.error("Error: Line formats have changed")
    #     return False

    print(f"line formats: {line_formats}")
    
    # ensure all line formats are present to make a valid CSP
    if len(line_formats) != 4:
        st.error("Error: Missing line formats. Reset the input")
        return False

    return True


def reset_text_area():
    print("resetting text area")
    load_input_file()
    st.session_state.from_user = False
    st.session_state.base_save_path = DEFAULT_RESULTS_ABSPATH
    st.session_state.input_text_area_key = str(uuid.uuid4())  # hack the widget key for updates
    # st.session_state.pop("input_text_area", None)
    
def graph_results():

    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    # Read data from CSV file
    df = pd.read_csv(st.session_state.result_csv_path)

    solve_container.write("Solution points")
    solve_container.write(df)

    # Create scatter plot using Plotly Express
    fig = go.Figure()

    print(df.columns)

    xcols = [col for col in df.columns if col.startswith("x")]
    alt_cols = [col for col in df.columns if (col.startswith("p") or col.startswith("y"))]

    print(f"xcols: {xcols}")
    print(f"alt_cols: {alt_cols}")

    trace1 = go.Scatter(x=df[xcols[0]], y=df[xcols[1]], mode='markers', name='x1 and x2')

    if len(alt_cols) > 1:
        trace2 = go.Scatter(x=df[alt_cols[0]], y=df[alt_cols[1]], mode='markers', name='p1 and p2')
    else:
        trace2 = go.Scatter(x=df[alt_cols[0]], y=df[alt_cols[0]], mode='markers', name='p1 and p2')
    # else:
    #     trace2 = go.Scatter(x=df[alt_cols[0]], y=df[alt_cols[0]], mode='markers', name='p1 and p2')

    #trace1 = go.Scatter(x=df['x1'], y=df['x2'], mode='markers', name='x1 and x2')
    #trace2 = go.Scatter(x=df['p1'], y=df['p2'], mode='markers', name='p1 and p2')

    fig.add_trace(trace1)
    fig.add_trace(trace2)

    # Customize the plot
    fig.update_layout(
        title=f'Optimization Results (n={len(df)})',
        xaxis_title='x',
        yaxis_title='y'
    )

    # Show the plot
    solve_container.plotly_chart(fig, use_container_width=True)





# init state
if 'input_text_area' not in st.session_state:
    st.session_state.input_text_area = ""
if 'previous_input_text_area' not in st.session_state:
    st.session_state.previous_input_text_area = ""
if 'problem_name' not in st.session_state:
    st.session_state.problem_name = ""
if 'solver_name' not in st.session_state:
    st.session_state.solver_name = ""
if 'from_user' not in st.session_state:
    st.session_state.from_user = False
if 'base_save_path' not in st.session_state:
    st.session_state.base_save_path = DEFAULT_RESULTS_ABSPATH
if 'result_csv_path' not in st.session_state:
    st.session_state.result_csv_path = ""
if 'previous_problem_name' not in st.session_state:
    st.session_state.previous_problem_name = ""
if 'input_text_area_key' not in st.session_state:
    st.session_state.input_text_area_key = str(uuid.uuid4())

print(st.session_state)


# App logic 

main_container = st.container()
main_container.title("Symbench CSP Solver")
problem_col, solver_col = main_container.columns([1, 1], gap="small")

problem_description_container = st.container()
problem_description_container.title("Problem Description")
solve_col, reset_col = problem_description_container.columns([1, 1], gap="small")

solve_container = st.container()
solve_container.title("Results")

graph_container = st.container()

# main container logic
with main_container:
    include_user_problems_checkbox = main_container.checkbox("List user-defined problems", value=False)

    problem_name_previous = st.session_state.problem_name
    solver_name_previous = st.session_state.solver_name

    if include_user_problems_checkbox:
        st.session_state.problem_name = problem_col.selectbox("Select a problem:", sorted([""] + [x + "_user" for x in PROBLEMS] + PROBLEMS))
    else:
        st.session_state.problem_name = problem_col.selectbox("Select a problem:", sorted([""] + PROBLEMS)) 

    st.session_state.solver_name = solver_col.selectbox("Select a solver:", SOLVERS)

    # reset past results on option change
    if st.session_state.solver_name != solver_name_previous:
        st.session_state.result_csv_path = ""

    if st.session_state.problem_name != problem_name_previous:
        st.session_state.result_csv_path = ""

# problem description container logic
with problem_description_container:

    if st.session_state.previous_problem_name != st.session_state.problem_name and st.session_state.problem_name != "":
        load_input_file()
        st.session_state.previous_problem_name = st.session_state.problem_name

    if st.session_state.problem_name != "":
        with st.expander("Edit Problem Description", expanded=True):
            input_text_area = st.text_area(
                "Each problem must contain at least 1 of 'variable', 'constraint', 'projection', and 'minimize/maximize'. Use Cmd or Ctrl + Enter to save changes",
                st.session_state.input_text_area,
                height=200,
                key=st.session_state.input_text_area_key,
                on_change=on_text_area_change,
            )

            if st.session_state.solver_name == "pymoo":
                num_generations = solve_col.slider("Number of generations", min_value=20, max_value=200, value=50, step=10, key="num_generations")
            elif st.session_state.solver_name == "constraint_prog":
                num_points = solve_col.slider("Number of points per iteration", min_value=100, max_value=10000, value=1000, step=1000, key="num_points")
                num_iters = reset_col.slider("Number of iterations", min_value=10, max_value=100, value=10, step=10, key="num_iters")


        reset_col.button("Reset Input", on_click=reset_text_area)

        
    
# solve container logic
with solve_container:

    if solve_col.button("Solve Problem"):
        with st.spinner(f"Solving {st.session_state.problem_name} with {st.session_state.solver_name}..."):
            solve_output = ""
            solve_progress_placeholder = st.empty()

            with st.expander("Solve Progress", expanded=True):
                start_time = time.time()
                if st.session_state.solver_name == "pymoo":
                    for solve_update in solve_problem(num_generations=num_generations):
                        solve_output += solve_update
                        solve_progress_placeholder.text_area("Solve Progress", solve_output, height=300)
                elif st.session_state.solver_name == "constraint_prog":
                    for solve_update in solve_problem(num_points=num_points, num_iters=num_iters):
                        solve_output += solve_update
                        solve_progress_placeholder.text_area("Solve Progress", solve_output, height=300)
                else:
                    for solve_update in solve_problem():
                        solve_output += solve_update
                        solve_progress_placeholder.text_area("Solve Progress", solve_output, height=300) 

                end_time = time.time()
                print(f" **** Solve time: {end_time - start_time} **** ")

with graph_container:
    if st.session_state.result_csv_path != "":
        with st.expander("Solution", expanded=True):
            with st.spinner("Saving results"):
                while not os.path.exists(st.session_state.result_csv_path):
                    time.sleep(1)
                graph_results()