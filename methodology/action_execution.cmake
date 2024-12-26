# Action execution methodology implementation
function(execute_action_phase)
    if(EXISTS "${REDLINE_CACHE_DIR}/work_queue/action_execution/complete")
        message(STATUS "Action execution phase already complete")
        return()
    endif()
    
    message(STATUS "Running action execution phase...")
    
    # Execute action execution agent
    execute_process(
        COMMAND ${CMAKE_BINARY_DIR}/action_execution_agent/action_execution_agent
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        RESULT_VARIABLE action_result
    )
    
    if(action_result EQUAL 0)
        file(WRITE "${REDLINE_CACHE_DIR}/work_queue/action_execution/complete" "")
        message(STATUS "Action execution phase complete")
    endif()
endfunction()
