import os

PROBLEMS = ["bnh", "osy", "tnk"] # das-cmop
SOLVERS = ["pymoo", "constraint_prog", "compare solutions"]
SCREENS = ["welcome", "problem-definitions", "symbench-dataset", "cp-problems-generator", "data view"]

PROBLEMS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-dataset", "symbench_dataset", "problems")
RESULTS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "results")
PROBLEM_SPECS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "problems")