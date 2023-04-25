import streamlit as st
from descriptions import PROBLEM_DESCRIPTIONS
import pages
from constants import PAGES



app_functions = {
    'Welcome': pages.welcome_page,
    'Problem Overview': pages.probdef_page,
    'Solve Problems': pages.symdata_page,
    'Generate Problems': pages.probgen_page,
    'View Results': pages.data_view_page
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