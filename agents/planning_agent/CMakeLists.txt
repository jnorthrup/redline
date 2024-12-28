# Include necessary CMake modules
include(../../cmake/LLMFunctions.cmake)
include(../../cmake/AgentFunctions.cmake)

# Set up environment management
setup_agent_environment()

# Use LLM-aware build target creation
llm_add_executable(planning_agent planning_agent.cpp)

# Use agent-specific build configuration
agent_add_executable(planning_agent planning_agent.cpp)

# Link libraries
target_link_libraries(planning_agent
    PRIVATE
        planning
        ${LLM_LIBRARIES}
        ${AGENT_LIBRARIES}
)
