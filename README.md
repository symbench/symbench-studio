# symbench studio

Initial setup of symbench studio for interactive exploration of relevant optimization problems

# Usage

0. clone this repository and `cd symbench-studio`
1. run `./setup.sh` (ideally in a python3 virtualn environment) to init submodules and install dependencies in development mode
2. from a terminal run `streamlit run spa.py`

# TODO 
- [ ] Send flag to `symbench-datset` to list configuration files to use (when available in symbench-dataset)
- [ ] Add `--history` option for `symbench-dataset` and display appropriately
- [ ] Add performance metrics
- [ ] Populate problem list, instead of a hard coded constant

## Current Selection Options
These values are configured in `constants.py`.

### Test Solvers Available

- pymoo
- constraint_prog 

### Test Problems Available

- "bnh"
- "disk" - plot not using p1/p2, but x/y/d/x1/y1 instead, so plot not providing good output
- "osy"
- "tnk"


