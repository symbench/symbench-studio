import streamlit as st
import actions 


def create_problem_solve():
    st.write("symbench-dataset submodule used:")
    symbench_dataset_link = "[symbench-dataset](https://github.com/symbench/symbench-dataset)"
    st.markdown(symbench_dataset_link, unsafe_allow_html=True)
    st.write("Here are the existing Symbench problems:")
    actions.problem_selection()
