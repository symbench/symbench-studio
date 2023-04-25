import streamlit as st
from constants import PROBLEMS
from descriptions import PROBLEM_DESCRIPTIONS
#from driver import call_solver
import actions

def probdef_page():
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

def probgen_page():
    st.write("cp-problems-generator screen")
    st.write("Here are the existing problems:")

    problems_to_generate = st.multiselect("Select problems to generate", PROBLEMS)
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

def symdata_page():
    st.write("symbench-dataset screen")
    st.write("Here are the existing Symbench problems:")
    actions.problem_selection()


def welcome_page():
    st.write("The following pages are available")
    st.write("- Problem Overview: view optimization problem objectives and constraints for BNH, OSY, TNK")
    st.write("- Generate Problems: create input.txt files which are consumed in the symbench-dataset screen to solve a selected optimization problem")
    st.write("- Solve Problems: solve a pre-defined problems with a selected solver using the input.txt file generated in the cp-problems-generator screen. Write results will be written to symbench-studio-data/results/ (need to modify write locations)")
    st.write("- View Results: view results from the symbench-studio-data/results/ folder")
    
    st.write("submodules used in this project:")
    symbench_dataset_link = "[symbench-dataset](git@github.com:symbench/symbench-dataset.git)"
    st.markdown(symbench_dataset_link, unsafe_allow_html=True)

    cp_problems_generator_link = "[cp-problems-generator](git@github.com:symbench/cp-problems-generator.git)"
    st.markdown(cp_problems_generator_link, unsafe_allow_html=True)

def data_view_page():
    st.write("data view page")


# def display_screen(screen):
#     if screen == "welcome":
#         welcome_screen()
#     elif screen == "cp-problems-generator":
#         probgen_screen()
#     elif screen == "symbench-dataset":
#         symdata_screen()
#     elif screen == "problem-definitions":
#         probdef_screen()
#     elif screen == "data view":
#         data_view_screen()
