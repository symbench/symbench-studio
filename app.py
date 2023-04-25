import streamlit as st
from pages.welcome import create_welcome
from pages.problem_overview import create_problem_overview
from pages.problem_solve import create_problem_solve
from pages.problem_generate import create_problem_generate
from pages.data_view import create_data_view
from constants import PAGES



app_functions = {
    'Welcome': create_welcome,
    'Problem Overview': create_problem_overview,
    'Generate Problems': create_problem_generate,
    'Solve Problems': create_problem_solve,
    'View Results': create_data_view
}

def create_sidebar():
    st.sidebar.title('Navigation')
    app_mode = st.sidebar.selectbox('Choose a page', PAGES)

    return app_mode

def main():
    st.set_page_config(layout="wide")

    st.title('Symbench Studio')

    app_mode = create_sidebar()
    app_functions[app_mode]()

if __name__ == '__main__':
    main()