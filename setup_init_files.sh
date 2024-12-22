#!/bin/bash

# Find all directories named "supervisor" and create an __init__.py file if it doesn't exist
find . -type d -name "supervisor" -exec touch {}/__init__.py \;
