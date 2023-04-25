import streamlit as st
from constants import PROBLEMS
from descriptions import PROBLEM_DESCRIPTIONS
#from driver import call_solver
import actions

def probdef_screen():
    problem_selection = st.selectbox("Select a problem:", PROBLEMS, index=0)
    problem_selection = problem_selection.lower()
    # solver_selection = st.selectbox("Select a solver:", SOLVERS, index=0)
    # visualize_results = st.checkbox("Visualize results?")

    if problem_selection is not None:
        objectives = PROBLEM_DESCRIPTIONS[problem_selection]["objectives"]
        constraints = PROBLEM_DESCRIPTIONS[problem_selection]["constraints"]

    st.write(f"{problem_selection} has objective(s):")

    for o in objectives:
        st.latex(o)

    st.write(f"Subject to constraint(s):")

    for c in constraints:
        st.latex(c)

def probgen_screen():
    st.write("cp-problems-generator screen")
    st.write("Here are the existing problems:")
    
    problems_to_generate = []
    for p in PROBLEMS:
        select_val = st.checkbox(p, value=False)
        if select_val:
            problems_to_generate.append(p)
    st.write(f"problems_to_generate: {problems_to_generate}")
    generate_button_press = st.button("Generate")
    if generate_button_press:
        with st.spinner("Generating..."):
            actions.problem_generation(problems_to_generate)



    if "das-cmop" in problems_to_generate:
        st.write("das-cmop selected")
        cmop_type = st.slider("Type", 1, 3, 1)
        cmop_difficulty = st.slider("Difficulty", 1, 15, 2)
        #cmop_gen_all = st.checkbox("Generate all DAS-CMOP problems?")

        # if cmop_gen_all:  # bool flag to generate selected
        #     actions.generate_selected_problems(problems_to_generate, True)
    actions.problem_generation(problems_to_generate)

def symdata_screen():
    st.write("symbench-dataset screen")
    st.write("Here are the existing Symbench problems:")
    actions.problem_selection()


def welcome_screen():
    st.write("Welcome to Symbench Studio")
    st.write("The following screens are available")
    st.write("- problem-definitions: view optimization problem objectives and constraints")
    st.write("- cp-problems-generator: generate new optimization problems")
    st.write("- symbench-dataset: solve and view results to defined problems")
    

def data_view_screen():
    st.write("data view screen")


def display_screen(screen):
    if screen == "welcome":
        welcome_screen()
    elif screen == "cp-problems-generator":
        probgen_screen()
    elif screen == "symbench-dataset":
        symdata_screen()
    elif screen == "problem-definitions":
        probdef_screen()
    elif screen == "data view":
        data_view_screen()
