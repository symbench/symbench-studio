import os

PROBLEMS = ["bnh", "osy", "tnk"] # das-cmop
SOLVERS = ["pymoo", "constraint_prog", "compare solutions"]
PAGES = ["Welcome", "Problem Overview", "Generate Problems", "Solve Problems", "View Results"]

PROBLEMS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-dataset", "symbench_dataset", "problems")
RESULTS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "results")
PROBLEM_SPECS_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-studio-data", "problems")