cmake_minimum_required(VERSION 3.10)

# Add the feedback loop agent executable
add_executable(feedback_loop_agent feedback_loop_agent.cpp)

# Add cache directory definition
target_compile_definitions(feedback_loop_agent 
    PRIVATE 
    REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}"
)
