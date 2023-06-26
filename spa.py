import streamlit as st
#from streamlit_ace import st_ace
import os
from constants import PROBLEMS, SOLVERS, SYMBENCH_DATASET_PATH, DEFAULT_RESULTS_ABSPATH, USER_RESULTS_ABSPATH, DEFAULT_PROBLEM_INPUTS_ABSPATH, USER_PROBLEM_INPUTS_ABSPATH

import re
import subprocess
import sys
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
import json



# allow continuous output from subprocess in streamlit text area
os.environ['PYTHONUNBUFFERED'] = '1'

DEFAULT_CONFIGS = {
    "pymoo": {
        "num_generations": 100
    },
    "constraint_prog": {
        "num_points": 10000,
        "num_of_iterations": 10
    }
}

def save_solver_config():
    """ store the results of the solve configuration in a json under the history folder """

    for solver in st.session_state.multiple_solvers + [st.session_state.solver_name]:

        print(f"solver is {solver}")
        
        solver_config = st.session_state.solver_config[solver]

        if solver in st.session_state.solver_config_name:
            solver_config_name = st.session_state.solver_config_name[solver]
        else:
            solver_config_name = "default"

        # assert isinstance(solver_config, dict)
        # assert solver_config != {}
        solver_config_filename = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, st.session_state.problem_name, f"{solver}_config.json")

        print(f"(save_solver_config) solver config: {solver_config}")
        print(f"(save_solver_config) saving configuration for {solver} to {solver_config_filename}")
        print(f"(save_solver_config) config file: {solver_config_filename}")

        if not os.path.exists(solver_config_filename):
            # config does not yet exist, create it with default
            os.makedirs(os.path.dirname(solver_config_filename), exist_ok=True)
            print(f"(save_solver_config) {solver_config_name, solver_config}")
            with open(solver_config_filename, 'w') as f:
                json.dump({"default" : DEFAULT_CONFIGS[solver]}, f, indent=3)
            
        else:  # config exists already, add to it
            # get current config
            current_config = {}
            if os.path.exists(solver_config_filename):
                with open(solver_config_filename, 'r') as f:
                    current_config = json.load(f)

            with open(solver_config_filename, 'w') as f:
                current_config.update({solver_config_name : solver_config})
                json.dump(current_config, f, indent=3)


def multi_solve_problem():
    """ called for solver comparison option """
    print("multi solve")

    solve_cmds = []
    for solver in st.session_state.multiple_solvers:
        settings = st.session_state.solver_config[solver]
        config_name = st.session_state.solver_config_name[solver]

        if solver == "pymoo":
            solve_cmd = f"symbench-dataset solve --problem {st.session_state.problem_name} --solver {solver} --config {config_name}" # --ngen {settings['num_generations']}"
        elif solver == "constraint_prog":
            solve_cmd = f"symbench-dataset solve --problem {st.session_state.problem_name} --solver {solver} --config {config_name}" #--num_points {settings['num_points']} --num_iters {settings['num_iters']}"
        
        if st.session_state.from_user:
            solve_cmd += " --user"
        solve_cmds.append((solver, solve_cmd))

    # set csv paths
    for solver in st.session_state.multiple_solvers:
        csv_path = os.path.join(st.session_state.base_save_path, solver, f"result_{st.session_state.problem_name}", f"{st.session_state.solver_config_name[solver]}.csv")
        st.session_state.result_csv_paths.append(csv_path)

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


def solve_problem(num_generations=None, num_points=None, num_iters=None):

    solver = st.session_state.solver_name
    problem = st.session_state.problem_name
    config_name = st.session_state.solver_config_name[solver]
    solve_cmd = f"symbench-dataset solve --problem {problem} --solver {solver} --config {config_name}"

    # if st.session_state.solver_name == "pymoo" and num_generations is not None:
    #     solve_cmd = solve_cmd # + f" --ngen {num_generations}"
    # elif st.session_state.solver_name == "constraint_prog" and num_points is not None and num_iters is not None:
    #     solve_cmd = solve_cmd + f" --num_points {num_points}" # --num_iters {num_iters}"
    
    if st.session_state.from_user:
        st.session_state.base_input_path = USER_PROBLEM_INPUTS_ABSPATH
        input_file_path = os.path.join(st.session_state.base_input_path, problem, "input.txt")
        solve_cmd += " --user"

    input_file_path = os.path.join(st.session_state.base_input_path, problem, "input.txt")
    
    print(f"solving problem with input file {input_file_path} using solver {solver}")
    print(f" ==== running command {solve_cmd.split(' ')}")

    process = subprocess.Popen(solve_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    print(f"st.session_state.solver_config_name: {config_name}")
    #solver_config_name = st.session_state.solver_config_name[st.session_state.solver_name]
    result_csv_path = os.path.join(st.session_state.base_save_path, solver, f"result_{problem}", f"{config_name}.csv")
    st.session_state.result_csv_path = result_csv_path
    print(f"result csv path is: {result_csv_path}")

    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            yield output.decode("utf-8")

    rc = process.poll()

    st.session_state.solve_complete = True

    return rc


def load_input_file():

    #if "_user" in problem_name:
    #    problem_name = problem_name.replace("_user", "")
    #    st.session_state.from_user = True
    #if st.session_state.from_user:
    file_path = os.path.join(st.session_state.base_input_path, st.session_state.problem_name, "input.txt")
    #else:
    #    file_path = os.path.join(DEFAULT_PROBLEM_INPUTS_ABSPATH, problem_name, "input.txt")
    print(f"loading default input file at: {file_path}")
    with open(file_path, "r") as f:
        content = f.read()
    validate_user_input(content)
    print(content)
    st.session_state.input_text_area = content


def save_user_modified_input_file(content):
    #if "_user" in st.session_state.problem_name:
    #    problem_name = st.session_state.problem_name.replace("_user", "")
    #if st.session_state.from_user:
    
    file_path = os.path.join(st.session_state.base_input_path, st.session_state.problem_name, "input.txt")
    
    # make the file at filepath if it does not exist
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
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
            st.session_state.from_user = True
            st.session_state.base_input_path = USER_PROBLEM_INPUTS_ABSPATH
            save_user_modified_input_file(content)
            st.session_state.base_save_path = USER_RESULTS_ABSPATH
            problem_description_container.write(f"Saved user modified file to {st.session_state.base_input_path}")
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

    print(f"line formats: {line_formats}")
    
    if len(line_formats) != 4:
        st.error("Error: Missing line formats. Reset the input")
        return False

    return True


def reset_text_area():
    print("resetting text area")
    st.session_state.base_input_path = DEFAULT_PROBLEM_INPUTS_ABSPATH
    load_input_file()
    st.session_state.from_user = False
    st.session_state.base_save_path = DEFAULT_RESULTS_ABSPATH
    st.session_state.input_text_area_key = str(uuid.uuid4())  # hack the widget key for updates
    # st.session_state.pop("input_text_area", None)
    
def graph_results(dfs, cols=None):
    """ plot a list of dfs """
    if not st.session_state.compare_solvers:  # single solver

        # Read data from CSV file

        # print(f"reading csv from: {st.session_state.result_csv_path}")
        # df = pd.read_csv(st.session_state.result_csv_path)

        #if len(dfs) == 1:
        df = dfs[0]
        solve_container.write("Solution points")
        solve_container.write(df)

        # scatter plot
        fig = go.Figure()

        print(f"columns: {df.columns}")

        alt_cols = [col for col in df.columns if col.startswith("p")]  #or col.startswith("y"))]

        print(f"alt_cols: {alt_cols}")

        if len(alt_cols) > 1:
            trace = go.Scatter(x=df[alt_cols[0]], y=df[alt_cols[1]], mode='markers', name='(p1, p2)')

        fig.add_trace(trace)

        # Customize the plot
        fig.update_layout(
            title=f'Solutions to {st.session_state.problem_name} solved with {st.session_state.solver_name} (num sols={len(df)})',
            xaxis_title='p1',
            yaxis_title='p2'
        )

        # Show the plot
        solve_container.plotly_chart(fig, use_container_width=True)

    else:
            #elif st.session_state.result_csv_paths and st.session_state.compare_solvers:  # multiple solvers
        # show the df of each result
            # df_list = []
            # for i, result_csv_path in enumerate(st.session_state.result_csv_paths):
            #     df = pd.read_csv(result_csv_path)
            #     df_list.append(df)
            #     multi_solver_cols[i].write(df)

            # plot each result on the same plot
        fig = go.Figure()

        # for each df, get alt_cols, and add trace to fig
        for i, df in enumerate(dfs):

            cols[i].write(df)

            alt_cols = [col for col in df.columns if col.startswith("p")]
            if len(alt_cols) > 1:
                trace = go.Scatter(x=df[alt_cols[0]], y=df[alt_cols[1]], mode='markers', name=f'{st.session_state.multiple_solvers[i]} (num sols={len(df)})')
                fig.add_trace(trace)

        # Customize the plot
        fig.update_layout(
            title=f'Solutions to {st.session_state.problem_name} solved with {st.session_state.multiple_solvers}',
            xaxis_title='p1',
            yaxis_title='p2'
        )

        # Show the plot
        solve_container.plotly_chart(fig, use_container_width=True)

# state

# user-editable area to adjust problem scpecification
if 'input_text_area' not in st.session_state:
    st.session_state.input_text_area = ""

# key to force update of text area
if 'previous_input_text_area' not in st.session_state:
    st.session_state.previous_input_text_area = ""

if 'problem_name' not in st.session_state:
    st.session_state.problem_name = ""

if 'solver_name' not in st.session_state:
    st.session_state.solver_name = ""

# default path to text inputs for the problem
if 'base_input_path' not in st.session_state: # todo path change
    st.session_state.base_input_path = DEFAULT_PROBLEM_INPUTS_ABSPATH

# user modified input file, which changes the path to results
if 'from_user' not in st.session_state:
    st.session_state.from_user = False

# default path to save results
if 'base_save_path' not in st.session_state: # todo path change
    st.session_state.base_save_path = DEFAULT_RESULTS_ABSPATH

# path to input file
if 'result_txt_path' not in st.session_state:
    st.session_state.result_txt_path = ""

# path to results csv file
if 'result_csv_path' not in st.session_state:
    st.session_state.result_csv_path = ""

# last selected problem
if 'previous_problem_name' not in st.session_state:
    st.session_state.previous_problem_name = ""

# unique text area key for re-renders
if 'input_text_area_key' not in st.session_state:
    st.session_state.input_text_area_key = str(uuid.uuid4())

# solve the same problem with multiple solver and compare results
if 'compare_solvers' not in st.session_state:
    st.session_state.compare_solvers = False

if 'multiple_solvers' not in st.session_state:
    st.session_state.multiple_solvers = []

if 'result_csv_paths' not in st.session_state:
    st.session_state.result_csv_paths = []

if 'solver_config' not in st.session_state:
    st.session_state.solver_config = {}

if 'solver_config_name' not in st.session_state:
    st.session_state.solver_config_name = {}

if 'solve_complete' not in st.session_state:
    st.session_state.solve_complete = False

print(st.session_state)


# App logic 

main_container = st.container()
main_container.title("Symbench Constraint Solver")
problem_col, solver_col = main_container.columns([1, 1], gap="small")
st.session_state.compare_solvers = solver_col.checkbox("Compare 2 or more solvers", value=False)

solver_config_container = st.container()
solver_config_container.header("Solver Configuration")

problem_description_container = st.container()
problem_description_container.title("Problem Description")

solve_container = st.container()
solve_container.title("Results")

# main container logic
with main_container:

    problem_name_previous = st.session_state.problem_name
    solver_name_previous = st.session_state.solver_name

    st.session_state.problem_name = problem_col.selectbox("Select a problem:", sorted(PROBLEMS)[::-1])

    with solver_config_container:
        if st.session_state.compare_solvers:  # multi selection
            st.session_state.multiple_solvers = solver_col.multiselect("Select solvers:", SOLVERS)
            if len(st.session_state.multiple_solvers) >= 2:
                multi_solver_cols = solver_config_container.columns(len(st.session_state.multiple_solvers))
                for i, solver_name in enumerate(st.session_state.multiple_solvers):
                    multi_solver_cols[i].subheader(solver_name)
                    if solver_name == "pymoo":
                        num_generations = multi_solver_cols[i].slider("# generations", min_value=20, max_value=100, step=5, value=50)
                        st.session_state.solver_config[solver_name] = {"num_generations": num_generations}
                        # checkbox for saving the config
                        with multi_solver_cols[i]:
                            if st.checkbox("Name this config", value=False, key=f"pymoo_solver_config_{i+1}"):
                                pymoo_config_name = st.text_input("Name this config:", key="pymoo_config", value="")
                                if pymoo_config_name == "default" or pymoo_config_name == "":
                                    st.warning("Config name can't be empty or 'default'")
                                else:
                                    st.session_state.solver_config_name[solver_name] = pymoo_config_name
                                    #if st.button("Save"):
                                        #save_solver_config()
                            else:
                                st.session_state.solver_config_name[solver_name] = "default"

                    elif solver_name == "constraint_prog":
                        num_points = multi_solver_cols[i].slider("# points per iteration", min_value=100, max_value=10000, value=1000, step=10, key="num_points")
                        num_iters = multi_solver_cols[i].slider("# iterations", min_value=10, max_value=100, value=10, step=5, key="num_iters")
                        st.session_state.solver_config[solver_name] = {"num_points": num_points, "num_of_iterations": num_iters}

                        with multi_solver_cols[i]:
                            if st.checkbox("Name this config", value=False, key=f"constraintprog_solver_config_{i+1}"):
                                constraint_prog_config_name = st.text_input("Name this config:", key="constraintprog_config", value="")
                                if constraint_prog_config_name == "default" or constraint_prog_config_name == "":
                                    st.warning("Config name can't be empty or 'default'")
                                else:
                                    st.session_state.solver_config_name[solver_name] = constraint_prog_config_name
                                    #if st.button("Save"):
                                        #save_solver_config()
                            else:
                                st.session_state.solver_config_name[solver_name] = "default"
                save_solver_config()
            else:
                st.error("Select at least 2 solvers to compare performance")
        else:  # single selection
            st.session_state.solver_name = solver_col.selectbox("Select a solver:", SOLVERS)
            solver_name = st.session_state.solver_name
            if solver_name == "pymoo":
                    num_generations = solver_config_container.slider("# generations", min_value=20, max_value=100, value=50)
                    st.session_state.solver_config[solver_name] = {"num_generations": num_generations}
            elif solver_name == "constraint_prog":
                num_points = solver_config_container.slider("# points per iteration", min_value=100, max_value=10000, value=1000, step=1000, key="num_points")
                num_iters = solver_config_container.slider("# iterations", min_value=10, max_value=100, value=10, step=10, key="num_iters")
                st.session_state.solver_config[solver_name] = {"num_points": num_points, "num_of_iterations": num_iters}

            if st.checkbox("Name this config", value=False, key="single_solver_config"):
                single_solver_config_name = st.text_input("Name this config:", value="")
                if single_solver_config_name == "default" or single_solver_config_name == "":
                    st.warning("Config name can't be empty or 'default'")
                else:
                    # set config name for selected solver
                    st.session_state.solver_config_name[solver_name] = single_solver_config_name
                    #if st.button("Save"):
            else:
                st.session_state.solver_config_name[solver_name] = "default"
            # else:  # session state default config name is 'default'
            #     save_solver_config()
            save_solver_config()

    # reset past results on option change - hacky state reset
    # if st.session_state.problem_name != problem_name_previous or st.session_state.solver_name != solver_name_previous:
    #     st.session_state.result_csv_path = ""
    #     st.session_state.result_csv_paths = []
    #     st.session_state.solve_complete = False
    #     st.session_state.compare_solvers = False
    #     st.session_state.multiple_solvers = []
    #     st.session_state.solver_name = ""
    #     st.session_state.solver_config = {}
    #     st.session_state.solver_config_name = {}


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

        solve_col, reset_col = problem_description_container.columns([1, 1], gap="small")
        #solve_col.button("Solve", on_click=solve_problem)
        reset_col.button("Reset Input", on_click=reset_text_area)

    with solve_container:

        if solve_col.button("Solve Problem"):
            if st.session_state.multiple_solvers:
                st.write(f"Solving {st.session_state.problem_name} with {st.session_state.multiple_solvers}...")
            else:
                st.write(f"Solving {st.session_state.problem_name} with {st.session_state.solver_name}...")
            with st.spinner():
                solve_output = ""
                solve_progress_placeholder = solve_container.empty()

                if st.session_state.compare_solvers is False:
                    with st.expander("", expanded=True):
                        start_time = time.time()
                        if st.session_state.solver_name == "pymoo":
                            for solve_update in solve_problem(num_generations=num_generations):
                                solve_output += solve_update
                                solve_progress_placeholder.text_area("", solve_output, height=300)
                        elif st.session_state.solver_name == "constraint_prog":
                            for solve_update in solve_problem(num_points=num_points, num_iters=num_iters):
                                solve_output += solve_update
                                solve_progress_placeholder.text_area("", solve_output, height=300)
                        else:
                            for solve_update in solve_problem():
                                solve_output += solve_update
                                solve_progress_placeholder.text_area("", solve_output, height=300) 
                        end_time = time.time()
                        print(f" **** Solve time: {end_time - start_time} **** ")

                        #with st.expander("Solver Performance", expanded=True):
    
                else:  # comparins multiple solvers
                    with st.expander("Solver Comparison", expanded=True):
                        multi_result_cols = solve_container.columns(len(st.session_state.multiple_solvers))
                        start_time = time.time()
                        solve_outputs = {solver_name: "" for solver_name in st.session_state.multiple_solvers}
                        solve_progress_placeholders = {solver_name: multi_result_cols[i].empty() for i, solver_name in enumerate(st.session_state.multiple_solvers)}

                        for solver_name, info_type, data in multi_solve_problem():
                            if info_type == "output":
                                solve_outputs[solver_name] += data
                                solve_progress_placeholders[solver_name].text_area(f"{solver_name} progress", solve_outputs[solver_name], height=300)

                                if "Execution time" in data:
                                    time_str = data.split("Execution time:")[1].split(" s")[0].strip()
                                    execution_time = float(time_str)
                                    st.session_state.solver_config[solver_name]["execution_time"] = execution_time
                        end_time = time.time()
                        print(f" **** Solve time: {end_time - start_time} **** ")
                        st.session_state.solve_complete = True

        with st.expander("Solver Performance", expanded=True):
            if st.session_state.compare_solvers and st.session_state.solve_complete:
                print("GRAPH")
                dfs = [pd.read_csv(result_csv_path) for result_csv_path in st.session_state.result_csv_paths]
                graph_results(dfs, cols=multi_solver_cols)
            elif st.session_state.result_csv_path and st.session_state.solve_complete:
                    df = pd.read_csv(st.session_state.result_csv_path)
                    graph_results([df])

        # if st.session_state.result_csv_paths and st.session_state.solve_complete:  # multi solver
        #     with st.expander("Solver Performance", expanded=True):
        #         
        # #if st.session_state.result_csv_path and st.session_state.solve_complete: # single solver
        # elif os.path.exists(st.session_state.result_csv_path) and st.session_state.solve_complete:
        #     with st.expander("Solver Performance", expanded=True):
        #         df = pd.read_csv(st.session_state.result_csv_path)
        #         graph_results([df])
