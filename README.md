# symbench studio

Initial setup of symbench studio for interactive exploration of relevant optimization problems

# Usage

0. clone this repository and `cd symbench-studio`
1. run `./setup.sh` (ideally in a python3 virtualn environment) to init submodules and install dependencies in development mode
2. from a terminal run `streamlit run spa.py`

# TODO 
- [x] write result to `symbench-studio-data`
- [x] Select by specific problem (e.g. circle packing) instead of optimization problem type
- [x] Display dataframe of solutions after solve completes
- [ ] Clean up/ speed up console writing to app interface
- [ ] visualization after solve or view Pareto fronts of previous solves

## Test Values
Currently, the test problems are:
- bnh
- disk

Test solvers are:
- pymoo
- constraint_prog 

one known error in sympy parsing for several circle in square problems: 
```
 ==== running command ['symbench-dataset', 'solve', '--problem', 'circles_in_square_7c', '--solver', 'pymoo']
Exception: unsupported operand type(s) for ^: 'Add' and 'Add'
ValueError: Error from parse_expr with transformed code: "Function ('geq' )((Symbol ('x0' )-Symbol ('x1' ))^Integer (2 )+(Symbol ('y0' )-Symbol ('y1' ))^Integer (2 )-(Symbol ('r0' )+Symbol ('r1' ))^Integer (2 ),Integer (0 ))"

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/michael/envs/symbench_studio/bin/symbench-dataset", line 33, in <module>
    sys.exit(load_entry_point('symbench-dataset', 'console_scripts', 'symbench-dataset')())
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/__main__.py", line 40, in run
    solver.main(args=sys.argv[2:])
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/solver.py", line 58, in main
    solve_problem(args.problem, args.solver)
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/solver.py", line 14, in solve_problem
    p.parse()
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/parser.py", line 24, in parse
    e = self._process_line(line[:-1])
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/parser.py", line 39, in _process_line
    e = elements.Constraint.from_string(line)
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/elements.py", line 107, in from_string
    return cls(name, expression, typing=typing)
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/elements.py", line 78, in __init__
    super().__init__(name, expression, typing=typing)
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/elements.py", line 51, in __init__
    self._expr = sympy.parse_expr(self.expression)
  File "/Users/michael/envs/symbench_studio/lib/python3.8/site-packages/sympy/parsing/sympy_parser.py", line 1101, in parse_expr
    raise e from ValueError(f"Error from parse_expr with transformed code: {code!r}")
  File "/Users/michael/envs/symbench_studio/lib/python3.8/site-packages/sympy/parsing/sympy_parser.py", line 1092, in parse_expr
    rv = eval_expr(code, local_dict, global_dict)
  File "/Users/michael/envs/symbench_studio/lib/python3.8/site-packages/sympy/parsing/sympy_parser.py", line 907, in eval_expr
    expr = eval(
  File "<string>", line 1, in <module>
TypeError: unsupported operand type(s) for ^: 'Add' and 'Add'
```

`Constraint-prog` solve with tnk
```
Traceback (most recent call last):
  File "/Users/michael/envs/symbench_studio/bin/symbench-dataset", line 33, in <module>
    sys.exit(load_entry_point('symbench-dataset', 'console_scripts', 'symbench-dataset')())
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/__main__.py", line 40, in run
    solver.main(args=sys.argv[2:])
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/solver.py", line 79, in main
    solve_problem(
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/solver.py", line 30, in solve_problem
    exec(f"{solver}.solve_problem(elements, problem, from_user, num_points=num_points, num_of_iterations=num_iters)")
  File "<string>", line 1, in <module>
  File "/Users/michael/darpa/symbench-studio/symbench-dataset/symbench_dataset/solvers/constraint_prog/solve.py", line 79, in solve_problem
    new_points = new_points.prune_pareto_front2(objectives)
  File "/Users/michael/darpa/symbench-studio/constraint-prog/constraint_prog/point_cloud.py", line 537, in prune_pareto_front2
    assert var in self.float_vars
AssertionError
 **** Solve time: 3.437432050704956 ****
 ```

 `Constraint prog` solve with Umesh1

 ```
 darpa/symbench-studio/symbench-dataset/symbench_dataset/solvers/constraint_prog/solve.py", line 86, in solve_problem
    points = new_points.projection(points.float_vars)
AttributeError: 'NoneType' object has no attribute 'projection'
 **** Solve time: 4.417096853256226 ****
 ```