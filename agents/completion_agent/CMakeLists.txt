# Include necessary CMake modules
include(../../cmake/LLMFunctions.cmake)
include(../../cmake/AgentFunctions.cmake)

# Set up environment management
setup_agent_environment()

# Use LLM-aware build target creation
llm_add_executable(completion_agent completion_agent.cpp)

# Use agent-specific build configuration
agent_add_executable(completion_agent completion_agent.cpp)

# Link libraries
target_link_libraries(completion_agent
    PRIVATE
        core
        ${LLM_LIBRARIES}
        ${AGENT_LIBRARIES}
)
