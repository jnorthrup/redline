cmake_minimum_required(VERSION 3.10)

# Add the completion agent executable
add_executable(completion_agent completion_agent.cpp)

# Add cache directory definition
target_compile_definitions(completion_agent 
    PRIVATE 
    REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}"
)
