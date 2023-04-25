import streamlit as st


def create_welcome():
    st.write("The following pages are available")
    st.write("- Problem Overview: view optimization problem objectives and constraints for BNH, OSY, TNK")
    st.write("- Generate Problems: create input.txt files which are consumed in the symbench-dataset screen to solve a selected optimization problem")
    st.write("- Solve Problems: solve a pre-defined problems with a selected solver using the input.txt file generated in the cp-problems-generator screen. Write results will be written to symbench-studio-data/results/ (need to modify write locations)")
    st.write("- View Results: view results from the symbench-studio-data/results/ folder")