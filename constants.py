import os

PROBLEMS = ["disk", "bnh", "osy", "tnk"] 
SOLVERS = ["pymoo", "constraint_prog"] #, "z3", "scipy"]
DEFAULT_CONFIGS = {
    "pymoo": {
        "pop_size": 100,
        "n_gen": 20
    },
    "constraint_prog": {
        "num_points": 1000,
        "num_of_iterations": 20
    }
}

# from config files, "n_gen" and "num_of_iterations" are simular and 
# "pop_size" and "num_points" are simular
NUM_ITERATIONS = {
    "min_value": 10,
    "max_value": 100,
    "default_value": 10,
    "step": 5,
    "key": "num_iters"
}

NUM_POINTS = {
    "min_value": 100,
    "max_value": 10000,
    "default_value": 1000,
    "step": 10,
    "key": "num_points"
}

CONFIG_SLIDER_SETTINGS = {
    "n_gen": NUM_ITERATIONS, 
    "num_of_iterations": NUM_ITERATIONS,
    "pop_size": NUM_POINTS, 
    "num_points": NUM_POINTS
}

SYMBENCH_DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbench-dataset", "symbench_dataset")
DEFAULT_RESULTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "results")
USER_RESULTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "user_results")
DEFAULT_PROBLEM_INPUTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "problems")
USER_PROBLEM_INPUTS_ABSPATH = os.path.join(SYMBENCH_DATASET_PATH, "user_problems")