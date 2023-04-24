#!/bin/bash
for dir in `ls -d */`; do
    cd "$dir"
    pip install -e .
    cd ..
done
