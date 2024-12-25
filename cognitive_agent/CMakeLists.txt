cmake_minimum_required(VERSION 3.10)

# Add the cognitive agent executable
add_executable(cognitive_agent cognitive_agent.cpp)

# Add cache directory definition
target_compile_definitions(cognitive_agent 
    PRIVATE 
    REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}"
)
