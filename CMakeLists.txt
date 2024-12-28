cmake_minimum_required(VERSION 3.10)

# Set policy for FindBoost removal
cmake_policy(SET CMP0167 NEW)

project(redline VERSION 1.0)

# Set CMAKE_PREFIX_PATH to help find dependencies
set(CMAKE_PREFIX_PATH
    "/usr/local"
    "/opt/local"
    "/usr"
    "/opt/homebrew"
    ENV CMAKE_PREFIX_PATH
)

# Include base CMake configuration
include(cmake/CMakeLists-base.txt)
include(cmake/LLMFunctions.cmake)
include(cmake/CharterTaskHandoff.cmake)
include(cmake/AgentFunctions.cmake)

# Find nlohmann_json library
find_package(nlohmann_json REQUIRED)

# Define project structure
add_subdirectory(src)
add_subdirectory(test)

# Add simple_program to the build
add_executable(simple_program src/simple_program.c)

# Additional configuration for LLM integration
include(CMakeLists-llm.txt)
