import streamlit as st
from constants import PROBLEMS
from descriptions import PROBLEM_DESCRIPTIONS
#from driver import call_solver
import actions

def create_problem_generate():
    st.write("cp-problems-generator submodule used:")
    cp_problems_generator_link = "[cp-problems-generator](https://github.com/symbench/cp-problems-generator)"
    st.markdown(cp_problems_generator_link, unsafe_allow_html=True)

    problems_to_generate = st.multiselect("Select one or more problems to generate", PROBLEMS)
    st.write(f"problems_to_generate: {problems_to_generate}")
    generate_button_press = st.button("Generate")
    if generate_button_press:
        with st.spinner("Generating..."):
            actions.problem_generation(problems_to_generate)



    if "das-cmop" in problems_to_generate:
        st.write("das-cmop selected")
        cmop_type = st.slider("Type", 1, 3, 1)
        cmop_difficulty = st.slider("Difficulty", 1, 15, 2)
        
    actions.problem_generation(problems_to_generate)
