import os

PROBLEMS = ["disk", "bnh", "osy", "tnk", "Harsh1", "Umesh1"] # "lever0"] # das-cmop
SOLVERS = ["pymoo", "constraint_prog"] #, "z3", "GA_simple", "scipy"]
#PAGES = ["Welcome", "Problem Overview", "Generate Problems", "Solve Problems", "View Results"]

#PROBLEMS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-dataset", "symbench_dataset", "problems")

SYMBENCH_DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-dataset", "symbench_dataset")

DEFAULT_RESULTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "results")
USER_RESULTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "user_results")
DEFAULT_PROBLEM_INPUTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "problems")
USER_PROBLEM_INPUTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "user_problems")