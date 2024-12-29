# Include necessary CMake modules
include(../../cmake/LLMFunctions.cmake)
include(../../cmake/AgentFunctions.cmake)
include(../../cmake/AgentCommonFunctions.cmake)

# Set up environment management
setup_agent_environment()

# Use LLM-aware build target creation
llm_add_executable(completion_agent completion_agent.cpp)

# Integrate run_cmake.sh conventions to protect LLM token counts
add_head_50_command(completion_agent)

# Use agent-specific build configuration
agent_add_executable(completion_agent completion_agent.cpp)

# Integrate run_cmake.sh conventions
add_custom_command(TARGET completion_agent POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "Running head -n 50 for command output"
    COMMAND ${CMAKE_COMMAND} -E echo "Example: head -n 50 output.txt"
)

# Link libraries
target_link_libraries(completion_agent
    PRIVATE
        core
        ${LLM_LIBRARIES}
        ${AGENT_LIBRARIES}
)
