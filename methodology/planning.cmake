# Planning methodology implementation
function(execute_planning_phase)
    if(EXISTS "${REDLINE_CACHE_DIR}/work_queue/planning/complete")
        message(STATUS "Planning phase already complete")
        return()
    endif()
    
    # Check if cognitive agent has completed
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/cognitive_agent/complete")
        message(STATUS "Waiting for cognitive agent to complete...")
        return()
    endif()
    
    message(STATUS "Running planning phase...")
    
    # Execute planning agent
    execute_process(
        COMMAND ${CMAKE_BINARY_DIR}/planning_agent/planning_agent
        RESULT_VARIABLE planning_result
    )
    
    if(planning_result EQUAL 0)
        file(WRITE "${REDLINE_CACHE_DIR}/work_queue/planning/complete" "")
        message(STATUS "Planning phase complete")
    else()
        message(FATAL_ERROR "Planning agent failed with error ${planning_result}")
    endif()
endfunction()