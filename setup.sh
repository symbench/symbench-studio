#!/bin/bash

# ensure submodules are updated
echo "Updating submodules..."
git submodule update --init

# ensure submodules are installed as packages
echo "Installing requirements..."
cd constraint-prog && pip install -e . && cd ..
cd symbench-dataset && pip install -e . && cd ..
cd cp-problems-generator && pip install -e . && cd ..

# install requirements
pip install -r requirements.txt
