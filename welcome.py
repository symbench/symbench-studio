import streamlit as st
#from pages.welcome import create_welcome
#from pages.1_problem_overview import create_problem_overview
#from pages.problem_solve import create_problem_solve
#from pages.problem_generate import create_problem_generate
#from pages.data_view import create_data_view
from constants import PAGES



#app_functions = {
#    'Welcome': create_welcome,
#    'Problem Overview': create_problem_overview,
#    'Generate Problems': create_problem_generate,
#    'Solve Problems': create_problem_solve,
#    'View Results': create_data_view
#}

def create_sidebar():
    st.sidebar.title('Navigation')
    app_mode = st.sidebar.selectbox('Choose a page', PAGES)

    return app_mode

def main():
    st.set_page_config(layout="wide")

    st.title('Symbench Studio')

    #app_mode = create_sidebar()
    #app_functions[app_mode]()
    #st.write("The following pages are available")
    #st.write("- **Problem Overview:** view optimization problem objectives and constraints for BNH, OSY, TNK")
    st.write("- **Problem Overview:** view optimization problem objectives and constraints")
    st.write("- **Generate Problems:** create ***input.txt*** files which are consumed in the ***problem solve*** page to solve a selected optimization problem")
    st.write("- **Solve Problems:** solve a pre-defined problems with a selected solver using the ***input.txt*** file generated in the ***problem generate*** screen") 

    st.write("- **View Results:** view results of the selected solved problem")
    st.write("")
    st.write("Results will be written to symbench-studio-data/results/ (need to modify write locations)")

if __name__ == '__main__':
    main()