function(run_agent AGENT_NAME INPUT OUTPUT_VAR)
    execute_process(
        COMMAND bash -c "&& ${AGENTS_ROOT}/${AGENT_NAME}/${AGENT_NAME} '${INPUT}'"
        OUTPUT_VARIABLE result
        RESULT_VARIABLE status
    )
    
    if(NOT status EQUAL 0)
        message(FATAL_ERROR "Agent ${AGENT_NAME} failed")
    endif()
    
    set(${OUTPUT_VAR} "${result}" PARENT_SCOPE)
endfunction()

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
