cmake_minimum_required(VERSION 3.10)

# Add the action execution agent executable
add_executable(action_execution_agent action_execution_agent.cpp)

# Add cache directory definition
target_compile_definitions(action_execution_agent 
    PRIVATE 
    REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}"
)
