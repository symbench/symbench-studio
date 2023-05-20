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


def solve_problem():
    if st.session_state.from_user:
        input_file_path = os.path.join(USER_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, "input.txt")
    else:
        input_file_path = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, "input.txt")
    st.write(f"solving problem with input file {input_file_path} using solver {st.session_state.solver_name}")

    if st.session_state.from_user: # check if we are handling a user-provided input
        solve_base_cmd = "symbench-dataset solve --problem [] --solver () --user"
    else:
        solve_base_cmd = "symbench-dataset solve --problem [] --solver ()"
    
    solve_cmd = solve_base_cmd.replace("[]", st.session_state.problem_name).replace("()", st.session_state.solver_name)
    print(f" ==== running command {solve_cmd.split(' ')}")
    st.write(f" ==== running command {solve_cmd}")
    process = subprocess.Popen(solve_cmd.split(" "), stdout=subprocess.PIPE)

    result_csv_path = os.path.join(st.session_state.base_save_path, st.session_state.solver_name, f"result_{st.session_state.problem_name}.csv")

    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            yield output.decode("utf-8")

    rc = process.poll()

    print(f"result csv path is: {result_csv_path}")

    if result_csv_path:
        solution_container = st.container()
        result_df = pd.read_csv(result_csv_path)
        solution_container.write(result_df)

    return rc


def load_default_input_file():
    file_path = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, "input.txt")
    print(f"loading default input file at: {file_path}")
    with open(file_path, "r") as f:
        content = f.read()
    print(content)
    st.session_state.input_text_area = content


def save_user_modified_input_file(content):
    file_path = os.path.join(USER_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, "input.txt")
    print(f"saving user modified input file at {file_path}")
    with open(file_path, "w") as f:
        f.write(content)
    st.session_state.from_user = True


def on_text_area_change():
    print("saving changes")
    content = st.session_state[st.session_state.input_text_area_key]
    if content != st.session_state.previous_input_text_area:
        result = validate_user_input(st.session_state.input_text_area)
        if result is not True:
            st.error(result)
        else:
            st.success("Valid input file")
            print(f"saving content: {st.session_state.input_text_area}")
            save_user_modified_input_file(content)
            st.session_state.from_user = True
            st.session_state.base_save_path = USER_RESULTS_ABSPATH
            st.write("Saved user modified file")
        st.session_state.previous_input_text_area = content

def validate_user_input(content):
    print("validating user input")
    input_str = content.strip().split("\n")
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
            st.error(f"Invalid format at line {line_number}: {line}")
            return False
        
        line_number += 1

    # If line formats change, return an error
    if len(line_formats) > 4: # You have 4 expected line formats
        st.error("Error: Line formats have changed")
        return False

    return True


def reset_text_area():
    print("resetting text area")
    load_default_input_file()
    st.session_state.from_user = False
    st.session_state.base_save_path = DEFAULT_RESULTS_ABSPATH
    st.session_state.input_text_area_key = str(uuid.uuid4())  # hack the widget key for updates
    # st.session_state.pop("input_text_area", None)
    
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
if 'previous_problem_name' not in st.session_state:
    st.session_state.previous_problem_name = ""
if 'input_text_area_key' not in st.session_state:
    st.session_state.input_text_area_key = str(uuid.uuid4())

print(st.session_state)


main_container = st.container()
main_container.title("Optimization Problem Solver")

# app logic
with main_container:
    include_user_problems_checkbox = main_container.checkbox("List user-defined problems", value=False)

    problem_col, solver_col = st.columns([1, 1])
    if include_user_problems_checkbox:
        st.session_state.problem_name = problem_col.selectbox("Select a problem:", sorted([""] + [x + "_user" for x in PROBLEMS])) #os.listdir(DEFAULT_PROBLEM_INPUTS_ABSPATH) + [x + "_user" for x in os.listdir(USER_PROBLEM_INPUTS_ABSPATH)]))
    else:
        st.session_state.problem_name = problem_col.selectbox("Select a problem:", sorted([""] + PROBLEMS))  #os.listdir(DEFAULT_PROBLEM_INPUTS_ABSPATH)))
    
    if st.session_state.previous_problem_name != st.session_state.problem_name:
        load_default_input_file()
        st.session_state.previous_problem_name = st.session_state.problem_name

    st.session_state.solver_name = solver_col.selectbox("Select a solver:", SOLVERS)

    st.write("Selected problem: ", st.session_state.problem_name)
    if st.session_state.problem_name != "":
        with st.expander("Input", expanded=True):
            # variable name collision fix
            input_text_area = st.text_area(
                "Edit Problem Desription:",
                st.session_state.input_text_area,
                height=300,
                key=st.session_state.input_text_area_key,
                on_change=on_text_area_change,
            )

            print(f"input text area: {input_text_area}")

        save_col, reset_col, solve_col = st.columns([0.5, 0.5, 0.5], gap="small")
        
        #save_col.button("Save Changes", on_click=on_save)
        
        reset_col.button("Reset Input", on_click=reset_text_area)
            # load_default_input_file()
            # st.session_state.input_text_area = st.session_state.input_text_area
            # st.session_state.input_text_area_key = str(uuid.uuid4())


        if solve_col.button("Solve Problem"):
            solve_output = ""
            solve_progress_placeholder = st.empty()

            print("solving problem")
            with st.expander("Solve Progress", expanded=True):
                for solve_update in solve_problem():
                    solve_output += solve_update
                    solve_progress_placeholder.text_area("Solve Progress", solve_output, height=300)
            print("solved problem")