# Include necessary CMake modules
include(cmake/LLMFunctions.cmake)
include(cmake/AgentFunctions.cmake)

# Define functions for LLM integration and command execution
function(llm_add_executable target)
  # LLM-aware build target creation
  add_executable(${target} ${ARGN})
  target_link_libraries(${target} PRIVATE ${LLM_LIBRARIES})
endfunction()

function(agent_add_executable target)
  # Agent-specific build configuration
  add_executable(${target} ${ARGN})
  target_link_libraries(${target} PRIVATE ${AGENT_LIBRARIES})
endfunction()

# Environment management
function(setup_agent_environment)
  if(NOT DEFINED ENV{OPENROUTER_API_KEY})
    message(FATAL_ERROR "Error: OPENROUTER_API_KEY environment variable not set")
  endif()
  # Load role-specific tools
  file(READ ${CMAKE_CURRENT_SOURCE_DIR}/scripts/${ROLE}_env.sh role_env)
  execute_process(COMMAND /bin/bash -c "${role_env}")
  # Load agent state
  file(READ ${CMAKE_CURRENT_SOURCE_DIR}/scripts/${AGENT_ID}_context.sh agent_context)
  execute_process(COMMAND /bin/bash -c "${agent_context}")
endfunction()

# Add subdirectories for each agent type
foreach(agent ${AGENT_TYPES})
    add_subdirectory(${agent})
endforeach()
