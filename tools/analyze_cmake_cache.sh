#!/bin/bash

# Script to analyze CMake cache files

echo "Analyzing CMake cache files..."

# Define an array of CMake cache file paths
declare -a cmake_cache_files=(
  "action_execution_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
  "cognitive_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
  "completion_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
  "feedback_loop_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
  "planning_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
)

# Loop through the files and print a summary
for file in "${cmake_cache_files[@]}"; do
  echo "----------------------------------------"
  echo "File: $file"
  echo "----------------------------------------"
  
  # Read the file and extract relevant information
  if grep -q "CMAKE_RELATIVE_PATH_TOP_SOURCE" "$file"; then
    source_path=$(grep "CMAKE_RELATIVE_PATH_TOP_SOURCE" "$file" | awk -F '"' '{print $2}')
    echo "CMAKE_RELATIVE_PATH_TOP_SOURCE: $source_path"
  fi
  if grep -q "CMAKE_RELATIVE_PATH_TOP_BINARY" "$file"; then
    binary_path=$(grep "CMAKE_RELATIVE_PATH_TOP_BINARY" "$file" | awk -F '"' '{print $2}')
    echo "CMAKE_RELATIVE_PATH_TOP_BINARY: $binary_path"
  fi
  if grep -q "CMAKE_FORCE_UNIX_PATHS" "$file"; then
    force_unix_paths=$(grep "CMAKE_FORCE_UNIX_PATHS" "$file" | awk '{print $2}')
    echo "CMAKE_FORCE_UNIX_PATHS: $force_unix_paths"
  fi
done

echo "----------------------------------------"
echo "CMake cache analysis complete."
echo "----------------------------------------"