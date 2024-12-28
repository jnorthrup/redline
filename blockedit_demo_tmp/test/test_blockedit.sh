#!/bin/bash

# Compile the test file
gcc -o test_blockedit test_blockedit.c -I../

# Run the test
./test_blockedit
