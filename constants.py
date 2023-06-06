import os

PROBLEMS = ["disk", "bnh", "osy", "tnk", "Harsh1", "Umesh1"] # "lever0"] # das-cmop
SOLVERS = ["pymoo", "constraint_prog"] #, "z3", "GA_simple", "scipy"]
#PAGES = ["Welcome", "Problem Overview", "Generate Problems", "Solve Problems", "View Results"]

#PROBLEMS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-dataset", "symbench_dataset", "problems")
DEFAULT_RESULTS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "results")
USER_RESULTS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "user-results")
DEFAULT_PROBLEM_INPUTS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "default-problems")
USER_PROBLEM_INPUTS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "user-problems")
CONFIG_HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "config-history")