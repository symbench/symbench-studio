#!/bin/bash

# ensure submodules are updated
echo "Updating submodules..."
git submodule update --init --recursive

# ensure submodules are installed as packages
echo "Installing requirements..."
for dir in `ls -d */`; do
    # ignore pycache and symbench-studio-data
    if [[ $dir == "__pycache__/" ]] || [[ $dir == "symbench-studio-data/" ]]; then
        continue
    fi
    cd "$dir"
    pip install -e .
    cd ..
done

# install requirements
pip install -r requirements.txt
