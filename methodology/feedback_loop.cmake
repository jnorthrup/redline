# Feedback loop methodology implementation
function(execute_feedback_phase)
    if(EXISTS "${REDLINE_CACHE_DIR}/work_queue/feedback/complete")
        message(STATUS "Feedback loop phase already complete")
        return()
    endif()
    
    # Check if action execution phase has completed
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/action_execution/complete")
        message(STATUS "Waiting for action execution phase to complete...")
        return()
    endif()
    
    message(STATUS "Running feedback loop phase...")
    
    # Execute feedback loop agent
    execute_process(
        COMMAND ${CMAKE_BINARY_DIR}/feedback_loop_agent/feedback_loop_agent
        RESULT_VARIABLE feedback_result
    )
    
    if(feedback_result EQUAL 0)
        file(WRITE "${REDLINE_CACHE_DIR}/work_queue/feedback/complete" "")
        message(STATUS "Feedback loop phase complete")
    elseif(feedback_result EQUAL 2)
        # Special return code 2 indicates need to iterate
        file(REMOVE "${REDLINE_CACHE_DIR}/work_queue/planning/complete")
        file(REMOVE "${REDLINE_CACHE_DIR}/work_queue/action_execution/complete")
        message(STATUS "Feedback loop requesting iteration - restarting from planning phase")
        execute_planning_phase()
    else()
        message(FATAL_ERROR "Feedback loop agent failed with error ${feedback_result}")
    endif()
endfunction()
