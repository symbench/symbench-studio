import streamlit as st
import os
import shutil
from constants import PROBLEMS_ABSPATH, SOLVERS


# Handle button actions
tmp_directory = "tmp"
if not os.path.exists(tmp_directory):
    os.mkdir(tmp_directory)


def load_input_file(problem_name):
    file_path = os.path.join(PROBLEMS_ABSPATH, problem_name, "input.txt")
    with open(file_path, "r") as f:
        content = f.read()
    return content


def save_tmp_input_file(problem_name, content):
    print("saving tmp file")
    tmp_file_path = os.path.join(tmp_directory, f"{problem_name}_input.txt")
    with open(tmp_file_path, "w") as f:
        f.write(content)

def on_text_area_change():
    save_tmp_input_file(problem_name, st.session_state.input_text_area)


main_container = st.container()
main_container.title("Optimization Problem Solver")
problem_name = main_container.selectbox("Select a problem:", os.listdir(PROBLEMS_ABSPATH), on_change=st.experimental_rerun)
input_file_content = load_input_file(problem_name)

# Initialize the session state for the input_text_area
if 'input_text_area' not in st.session_state:
    st.session_state.input_text_area = load_input_file(problem_name)

# Add the text area with the session state value
input_text_area = st.text_area("Edit the input file:", st.session_state.input_text_area, key="input_text_area", on_change=on_text_area_change)

# Add action buttons
reset_button = main_container.button("Reset to Original")

if reset_button:
    print("resetting")
    st.session_state.input_text_area = load_input_file(problem_name)
    st.experimental_rerun()

# # Add a container for the solver
# solver_container = st.container()

# # Add solver selection and execution
# with solver_container.expander("Select Solver"):
#     solver = st.selectbox("Choose a solver:", SOLVERS, index=0)
#     run_solver_button = st.button("Run Solver")