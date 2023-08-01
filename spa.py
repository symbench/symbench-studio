import streamlit as st
#from streamlit_ace import st_ace
import os
from constants import SOLVERS, DEFAULT_CONFIGS, NUM_POINTS, NUM_ITERATIONS, CONFIG_SLIDER_SETTINGS
from constants import SYMBENCH_DATASET_PATH, DEFAULT_RESULTS_ABSPATH, DEFAULT_PROBLEM_INPUTS_ABSPATH

import re
import subprocess
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
import json


# allow continuous output from subprocess in streamlit text area
os.environ['PYTHONUNBUFFERED'] = '1'


def save_solver_config():
    """ store the results of the solve configuration in a json under the history folder """

    all_solvers = st.session_state.multiple_solvers if st.session_state.compare_solvers else [st.session_state.solver_name]
    for solver in all_solvers:
        print(f"solver is {solver}")
        solver_config = st.session_state.all_configs[solver]
        solver_config_filename = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, f"{solver}_config.json")
        print(f"(save_solver_config) saving configuration for {solver} to {solver_config_filename}")

        if not os.path.exists(solver_config_filename):
            # config does not yet exist, create it with default
            os.makedirs(os.path.dirname(solver_config_filename), exist_ok=True)
        
        print(f"(save_solver_config) {solver_config}")
        with open(solver_config_filename, 'w') as f:
            json.dump(solver_config, f, indent=3)

def multi_solve_problem():
    """ called for all solvers requested """
    print("solve problem ...")

    solve_cmds = []
    all_solvers = st.session_state.multiple_solvers if st.session_state.compare_solvers else [st.session_state.solver_name]
    #print(f"DEBUG: all solvers: {all_solvers}")
    for solver in all_solvers:
        solver_config_names = ",".join(st.session_state.selected_config_names[solver])
        solve_cmd = f"symbench-dataset solve --problem {st.session_state.problem_name} --solver {solver} --configs {solver_config_names}"
        if st.session_state.history_request:
            solve_cmd = solve_cmd + " --history"
        print(f"(solve command) {solve_cmd}")
        solve_cmds.append((solver, solve_cmd))

    # set csv paths
    #print("DEBUG: setup csv paths ...")
    st.session_state.result_csv_paths = []
    for solver in all_solvers:
        for config in st.session_state.selected_config_names[solver]:
            if st.session_state.history_request:
                csv_path = os.path.join(st.session_state.base_save_path, solver, f"result_{st.session_state.problem_name}", f"{config}_hist.csv")
            else:
                csv_path = os.path.join(st.session_state.base_save_path, solver, f"result_{st.session_state.problem_name}", f"{config}.csv")
            st.session_state.result_csv_paths.append(csv_path)
    print(f"DEBUG: full csv path: {st.session_state.result_csv_paths}")

    def run_commands(solve_cmds):
        processes = []
        output_generators = []
        solver_mapping = {}
        start_times = {}

        for solver, cmd in solve_cmds:
            process = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            processes.append(process)
            output_generators.append(iter(process.stdout.readline, b''))
            solver_mapping[process] = solver
            start_times[process] = time.time()

        while processes:
            for i, process in enumerate(processes):
                try:
                    line = next(output_generators[i])
                    solver_name = solver_mapping[process]
                    yield (solver_name, "output", line.decode("utf-8"))
                except StopIteration:
                    process.communicate()
                    end_time = time.time()
                    solver_name = solver_mapping[process]
                    elapsed_time = end_time - start_times[process]
                    #yield (solver_name, "time", elapsed_time)
                    processes.remove(process)
                    output_generators.pop(i)
                    del solver_mapping[process]
                    del start_times[process]
                    break

    return run_commands(solve_cmds)

def find_problem_names(root_directory):
    problem_names = []
    for root, _, files in os.walk(root_directory):
        if "input.txt" in files:
            relative_path = os.path.relpath(root, root_directory)
            problem_names.append(relative_path.replace(os.path.sep, '/'))
    return problem_names

def load_input_file():
    file_path = os.path.join(st.session_state.base_input_path, st.session_state.problem_name, "input.txt")
    print(f"loading default input file at: {file_path}")
    with open(file_path, "r") as f:
        content = f.read()
    validate_user_input(content)
    print(content)
    st.session_state.input_text_area = content

def load_config_file(solver):
    config_file_path = os.path.join(st.session_state.base_input_path, st.session_state.problem_name, f"{solver}_config.json")
    current_config = {}
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            current_config = json.load(f)
    else:
        print(f"config file: {config_file_path} does not exist")
    return current_config

# Configuration file adjustment area
def create_config_tabs(solver_name, config_column):
    config_items = {}
    if solver_name not in st.session_state.config_tabs_present.keys():
        config_items = load_config_file(solver_name)
        st.session_state.all_configs[solver_name] = config_items
        st.session_state.config_tabs_present[solver_name] = True
        st.session_state.new_config[solver_name] = False
    else:
        config_items = st.session_state.all_configs[solver_name]
    
    if config_column.button("Add New Config", key="new_config"+solver_name):
        st.session_state.new_config[solver_name] = True
    if st.session_state.new_config[solver_name]:
        requested_solver_config_name = config_column.text_input("Name this config:", value="", key="new_config_name"+solver_name)
        if requested_solver_config_name == "default" or requested_solver_config_name == "":
            config_column.warning("Config name can't be empty or 'default'")
        else:
            default_config_set = DEFAULT_CONFIGS[solver_name].copy()
            st.session_state.all_configs[solver_name][requested_solver_config_name] = default_config_set
            st.session_state.new_config[solver_name] = False
            config_column.success(f"New configuration added for {solver_name}")

    if st.session_state.all_configs[solver_name]:
        st.session_state.selected_config_names[solver_name] = config_column.multiselect("Select Configs:", st.session_state.all_configs[solver_name].keys())
        config_column.write("Configuration Options Selected:")
        if (len(st.session_state.selected_config_names[solver_name]) >= 1):
            tabs = config_column.tabs(st.session_state.selected_config_names[solver_name])
            for config_tab, config_name in zip(tabs, st.session_state.selected_config_names[solver_name]):
                config_content = config_items[config_name]
                with config_tab:
                    for config_slider in config_content:
                        if config_slider in CONFIG_SLIDER_SETTINGS:
                            config_slider_value = config_tab.slider(config_slider, min_value=CONFIG_SLIDER_SETTINGS[config_slider]["min_value"], max_value=CONFIG_SLIDER_SETTINGS[config_slider]["max_value"], value=int(config_content[config_slider]), step=CONFIG_SLIDER_SETTINGS[config_slider]["step"], key=CONFIG_SLIDER_SETTINGS[config_slider]["key"]+solver_name+config_name)
                            st.session_state.all_configs[solver_name][config_name][config_slider] = config_slider_value
                        else:
                            st.error(f"Unknown configuration key: {config_slider}")
                            slider_options = [key for key in CONFIG_SLIDER_SETTINGS]
                            st.error(f"Available options are: {slider_options}")
                            
        #print(f"DEBUG (create config): @@@@@@@@@ all_configs: {st.session_state.all_configs}")
        #print(f"DEBUG (create config): config_items: {config_items}")
        #print(f"DEBUG (create config): config_tabs_present: {st.session_state.config_tabs_present}")
        #print(f"DEBUG (create config): selected_config_names: {st.session_state.selected_config_names}")
    else:
        config_column.warning(f"No configuration file available for {solver_name}")

def save_user_modified_input_file(content):
    file_path = os.path.join(st.session_state.base_input_path, st.session_state.problem_name, "input.txt")
    
    # make the file at filepath if it does not exist
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(content)

def on_text_area_change():
    print("saving changes")
    content = st.session_state[st.session_state.input_text_area_key]
    if content != st.session_state.previous_input_text_area:
        result = validate_user_input(content)
        if result is True:
            problem_description_container.success("Valid input file")
            print(f"saving content: {st.session_state.input_text_area}")
            save_user_modified_input_file(content)
            problem_description_container.write(f"Saved user modified file to {st.session_state.base_input_path}")
        st.session_state.previous_input_text_area = content

def validate_user_input(content):
    print("validating user input")

    input_str = [line for line in content.strip().split("\n") if line != ""]

    line_number = 1
    
    variable_pattern = re.compile(r'^variable\s+\w+\s+-?\d+(\.\d+)?\s+-?\d+(\.\d+)?$')
    constraint_pattern = re.compile(r'^constraint\s+\w+\s+(leq|geq)\(.+?\)$')
    projection_pattern = re.compile(r'^projection\s+\w+\s+.+$')
    optimize_pattern = re.compile(r'^(minimize|maximize)\s+\w+$')
    ext_function_pattern = re.compile(r'^ext_function\s+\w+\(\d+\)\s+\w+\.pt$') 
    derivative_pattern = re.compile(r'^derivative\s+\w+\s+.+$')
    
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
        elif ext_function_pattern.match(line):
            line_formats.add('ext_function')
        elif derivative_pattern.match(line):
            line_formats.add('derivative')
        else:
            problem_description_container.error(f"Invalid format at line {line_number}: {line}")
            return False
        
        line_number += 1

    print(f"line formats: {line_formats}")
    
    if len(line_formats) < 4:  # might need to update
        st.error("Error: Missing line formats. Reset the input")
        return False

    return True

def graph_results(dfs, cols=None):
    """ plot a list of dfs """
    
    fig = go.Figure()

    # for each df, get alt_cols, and add trace to fig
    # Create tabs for the different configurations within the cols provided
    all_solvers = st.session_state.multiple_solvers if st.session_state.compare_solvers else [st.session_state.solver_name]
    all_result_tabs = {}
    for col_num, col in enumerate(cols):
        result_tabs = col.tabs(st.session_state.selected_config_names[all_solvers[col_num]])
        all_result_tabs[col_num] = result_tabs
        
    dataset_expected = 0
    alt_cols = []
    for solver in all_solvers:
        dataset_expected += len(st.session_state.selected_config_names[solver]) 
    #print(f"DEBUG: dataset_expected = {dataset_expected}, number columns: {len(cols)}, length of DFS = {len(dfs)}")
    if dataset_expected == len(dfs):            
        df_index = 0
        df = []
        for col_num, tabs in all_result_tabs.items():
            for tab_num, tab in enumerate(tabs):
                if df_index >= len(dfs):
                    print("More solutions available then tabs available to display")
                    break

                df = dfs[df_index]
                tab.write("Solution Points:")
                tab.write(df)
                
                alt_cols = df.columns[-2:]
                if len(alt_cols) > 1:
                    trace = go.Scatter(x=df[alt_cols[0]], y=df[alt_cols[1]], mode='markers', name=f'{all_solvers[col_num]}: {st.session_state.selected_config_names[all_solvers[col_num]][tab_num]} (num sols={len(df)})')
                    fig.add_trace(trace)
                
                df_index +=1
                #print(f"DEBUG: tab_num={tab_num}, col_num={col_num}, df_index={df_index}, len(tabs)={len(tabs)}")
    else:
        print("Warning: Data and column/tab expection does not match")

    # Customize the plot
    fig.update_layout(
        title=f'Solutions to {st.session_state.problem_name} solved with {all_solvers}',
        xaxis_title=alt_cols[0],
        yaxis_title=alt_cols[1]
    )

    # Show the plot
    solve_container.plotly_chart(fig, use_container_width=True)


#################
# System States
#################

# selected problem name
if 'problem_name' not in st.session_state:
    st.session_state.problem_name = ""
    
# last selected problem
if 'previous_problem_name' not in st.session_state:
    st.session_state.previous_problem_name = ""
    
# Used to add textbox when "Add new problem" button is pressed
if 'new_problem' not in st.session_state:
    st.session_state.new_problem = False

# solve the same problem with multiple solver and compare results
if 'compare_solvers' not in st.session_state:
    st.session_state.compare_solvers = False

# selected solver name (when only one selected, not comparing)
if 'solver_name' not in st.session_state:
    st.session_state.solver_name = ""

# selected solvers when comparing
if 'multiple_solvers' not in st.session_state:
    st.session_state.multiple_solvers = []

# all configurations from the input file and the added configurations during setup
if 'all_configs' not in st.session_state:
    st.session_state.all_configs = {}

# configuration names selected for each solver selected
if 'selected_config_names' not in st.session_state:
    st.session_state.selected_config_names = {}

# Used to add textbox and warnings when "Add new config" button is pressed
if 'new_config' not in st.session_state:
    st.session_state.new_config = {}

# Indicate when config tab is first being created to allow loading data from a file
if 'config_tabs_present' not in st.session_state:
    st.session_state.config_tabs_present = {}

# default path to text inputs for the problem
if 'base_input_path' not in st.session_state: # todo path change
    st.session_state.base_input_path = DEFAULT_PROBLEM_INPUTS_ABSPATH

# default path to save results
if 'base_save_path' not in st.session_state: # todo path change
    st.session_state.base_save_path = DEFAULT_RESULTS_ABSPATH

# user-editable area to adjust problem specification
if 'input_text_area' not in st.session_state:
    st.session_state.input_text_area = ""

# key to force update of text area
if 'previous_input_text_area' not in st.session_state:
    st.session_state.previous_input_text_area = ""

# unique text area key for re-renders
if 'input_text_area_key' not in st.session_state:
    st.session_state.input_text_area_key = str(uuid.uuid4())
    
# user requests to show solve history (uses --history flag when solving problem)
if 'history_request' not in st.session_state:
    st.session_state.history_request = False

# List of paths for the solved csv file (per selected solver/configs)
if 'result_csv_paths' not in st.session_state:
    st.session_state.result_csv_paths = []

# signals completion of solve command, reset after graphing of data is complete
if 'solve_complete' not in st.session_state:
    st.session_state.solve_complete = False

# Store metrics for the selected solvers
#   Current metrics: execution time (for solvers that provide this information)
if 'solver_metrics' not in st.session_state:
    st.session_state.solver_metrics = {}

print(st.session_state)


# App logic 
st.set_page_config(layout="wide")
main_container = st.container()
main_container.title("Symbench Constraint Solver")
problem_col, solver_col = main_container.columns([1, 1], gap="small")
st.session_state.compare_solvers = solver_col.checkbox("Compare 2 or more Solvers", value=False)

solver_config_container = st.container()
solver_config_container.header("Solver Configuration")

problem_description_container = st.container()
problem_description_container.header("Problem Description")

solve_container = st.container()
solve_container.header("Results")

# main container logic
with main_container:
    problem_name_previous = st.session_state.problem_name
    problem_names_list = find_problem_names(DEFAULT_PROBLEM_INPUTS_ABSPATH)
    
    # Create button to allow user to create a new problem
    if problem_col.button("Add New Problem", key="new_prob_button"):
        st.session_state.new_problem = True
        st.session_state.problem_name = ""
    if st.session_state.new_problem:
        new_prob_name = problem_col.text_input("Name the new problem (can include subdirectory):", value="", key="new_prob_input")
        new_prob_dir = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, new_prob_name)
        if new_prob_name in problem_names_list:
            problem_col.warning(f"Problem named {new_prob_name} already exists")
        elif new_prob_name != "":
            # Add folder for new problem with blank problem description
            os.makedirs(new_prob_dir, exist_ok=True)
            new_prob_full_name = os.path.join(new_prob_dir, "input.txt")
            with open(new_prob_full_name, mode="w") as f:
                pass
            problem_names_list.append(new_prob_name)
            st.session_state.new_problem = False
            problem_col.success(f"New blank problem added for {new_prob_name}, please fill in the problem definition")

    st.session_state.problem_name = problem_col.selectbox("Select a Problem:", sorted(problem_names_list)[::])
    if st.session_state.problem_name != problem_name_previous:
        st.session_state.config_tabs_present = {}
        st.session_state.all_configs = {}

    with solver_config_container:
        if st.session_state.compare_solvers:  # multi selection
            st.session_state.multiple_solvers = solver_col.multiselect("Select solvers:", SOLVERS)
            if len(st.session_state.multiple_solvers) >= 2:
                multi_solver_cols = solver_config_container.columns(len(st.session_state.multiple_solvers))
                for i, solver_name in enumerate(st.session_state.multiple_solvers):
                    multi_solver_cols[i].subheader(solver_name)
                    create_config_tabs(solver_name, multi_solver_cols[i])
            else:
                st.error("Select at least 2 solvers to compare performance")
        else:  # single selection
            st.session_state.solver_name = solver_col.selectbox("Select a solver:", SOLVERS)
            solver_name = st.session_state.solver_name
            multi_solver_cols = solver_config_container.columns(1)
            multi_solver_cols[0].subheader(solver_name)
            # Select configurations to use
            create_config_tabs(solver_name, multi_solver_cols[0])

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

        solve_col, history_col = problem_description_container.columns([1, 1], gap="small")
        st.session_state.history_request = history_col.checkbox("Request Solve History", value=False)

    with solve_container:

        if solve_col.button("Solve Problem"):
            save_solver_config()
            all_solvers = st.session_state.multiple_solvers if st.session_state.compare_solvers else [st.session_state.solver_name]
            st.write(f"Solving {st.session_state.problem_name} with {all_solvers}...")
            with st.spinner():
                solve_output = ""
                solve_progress_placeholder = solve_container.empty()

                with st.expander("Solver Output", expanded=True):
                    # Setup columns for the different solvers                        
                    multi_result_cols = solve_container.columns(len(all_solvers))
                    start_time = time.time()
                    solve_outputs = {solver_name: "" for solver_name in all_solvers}
                    solve_progress_placeholders = {solver_name: multi_result_cols[i].empty() for i, solver_name in enumerate(all_solvers)}

                    for solver_name, info_type, data in multi_solve_problem():
                        if info_type == "output":
                            solve_outputs[solver_name] += data
                            solve_progress_placeholders[solver_name].text_area(f"{solver_name} progress", solve_outputs[solver_name], height=300)

                            if "Execution time" in data:
                                time_str = data.split("Execution time:")[1].split(" s")[0].strip()
                                execution_time = float(time_str)
                                st.session_state.solver_metrics[solver_name]= {"execution_time": execution_time}
                                #print(f"DEBUG: solver_metrics: {st.session_state.solver_metrics}")
                    end_time = time.time()
                    print(f" **** Solve time: {end_time - start_time} seconds **** ")
                    st.session_state.solve_complete = True

        with st.expander("Solver Performance", expanded=True):
            if st.session_state.solve_complete:
                print("GRAPH")
                dfs = []
                dfs = [pd.read_csv(result_csv_path) for result_csv_path in st.session_state.result_csv_paths]
                #print(f"DEBUG: dfs: {dfs}")
                graph_results(dfs, cols=multi_result_cols)
                    
                # reset solve complete flag
                st.session_state.solve_complete = False

