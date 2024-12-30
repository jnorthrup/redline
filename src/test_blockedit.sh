#!/usr/bin/env bash

# Enable detailed debugging
set -vx

# Source the blockedit.sh script to set environment variables
source src/blockedit.sh

# Define the test file and the new text to insert
TEST_FILE="src/testfile.txt"
NEW_TEXT="This is the new text inserted by the blockedit script."

# Ensure the output log file exists with the correct permissions
touch src/output.log
chmod 666 src/output.log

# Call the edit function to modify the test file
./src/blockedit.sh edit "$TEST_FILE" "$NEW_TEXT" 2 3

# Call the verify function to ensure the changes were made correctly
./src/blockedit.sh verify "$TEST_FILE" "$TEST_FILE" 2 3

# Check the output log for verification
if grep -q "No differences found between files in the specified range." src/output.log; then
  echo "Test passed: The blockedit script successfully edited and verified the file."
else
  echo "Test failed: The blockedit script did not edit or verify the file correctly."
fi

# Explicitly log the contents of output.log
echo "Contents of output.log:" | tee -a src/output.log
cat src/output.log | tee -a src/output.log

# Additional logging for debugging
echo "Test case completed." | tee -a src/output.log
echo "Final contents of $TEST_FILE:" | tee -a src/output.log
cat "$TEST_FILE" | tee -a src/output.log

# Disable debugging
set +vx
