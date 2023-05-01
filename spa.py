import streamlit as st
import os
import shutil
from constants import PROBLEM_INPUTS_ABSPATH, USER_PROBLEM_INPUTS, SOLVERS

import re
import subprocess


def solve_problem(problem_name, solver_name):
    if st.session_state.user_modified:
        input_file_path = os.path.join(USER_PROBLEM_INPUTS, problem_name, "user_input.txt")
    else:
        input_file_path = os.path.join(PROBLEM_INPUTS_ABSPATH, problem_name, "input.txt")
    st.write(f"solving problem with input file {input_file_path} using solver {solver_name}")

def load_input_file(problem_name):
    file_path = os.path.join(PROBLEM_INPUTS_ABSPATH, problem_name, "input.txt")
    with open(file_path, "r") as f:
        content = f.read()
    return content


def save_user_modified_input_file(problem_name, content):
    print("saving user modified file")
    tmp_file_path = os.path.join(USER_PROBLEM_INPUTS, problem_name, "user_input.txt")
    with open(tmp_file_path, "w") as f:
        f.write(content)
    st.session_state.from_user = True


def on_text_area_change():
    result = validate_user_input_file()
    if result is not True:
        st.error(result)
    else:
        st.success("Valid input file")
        save_user_modified_input_file(problem_name, st.session_state.input_text_area)
        st.session_state.user_modified = True
        st.write("Saved user modified file")

def validate_user_input_file():
    
    input_str = st.session_state.input_text_area.strip().split("\n")
    line_number = 1
    
    variable_pattern = re.compile(r'^variable\s+\w+\s+-?\d+(\.\d+)?\s+-?\d+(\.\d+)?$')
    constraint_pattern = re.compile(r'^constraint\s+\w+\s+(leq|geq)\(.+\,-?\d+(\.\d+)?\)$')
    projection_pattern = re.compile(r'^projection\s+\w+\s+.+$')
    optimize_pattern = re.compile(r'^(minimize|maximize)\s+\w+$')

    for line in input_str:
        if not (variable_pattern.match(line) or constraint_pattern.match(line) 
                or projection_pattern.match(line) or optimize_pattern.match(line)):
            return f"Invalid format at line {line_number}: {line}"
        line_number += 1
    
    return True

def reset_text_area():
    st.session_state.input_text_area = load_input_file(problem_name)
    st.session_state.user_modified = False



st.session_state.from_user = False  # assume original problem will be solved

main_container = st.container()
main_container.title("Optimization Problem Solver")
problem_name = main_container.selectbox("Select a problem:", os.listdir(PROBLEM_INPUTS_ABSPATH))
input_file_content = load_input_file(problem_name)

# Initialize the session state for the input_text_area
if 'input_text_area' not in st.session_state:
    st.session_state.input_text_area = load_input_file(problem_name)
    st.session_state.user_modified = False

input_text_area = st.text_area("Edit the input file:", st.session_state.input_text_area, height=500, key="input_text_area", on_change=on_text_area_change)
reset_button = main_container.button("Reset to Original", on_click=lambda: st.session_state.pop("input_text_area", None))
validate_button = main_container.button("Validate Input File", on_click=validate_user_input_file)

solver_selection = main_container.selectbox("Select a solver:", SOLVERS)
solve_button = main_container.button("Solve", on_click=lambda: solve_problem(problem_name, solver_selection))