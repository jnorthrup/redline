# Completion methodology implementation
function(execute_completion_phase)
    if(EXISTS "${REDLINE_CACHE_DIR}/work_queue/completion/complete")
        message(STATUS "Completion phase already complete")
        return()
    endif()
    
    # Check if feedback loop phase has completed
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/feedback/complete")
        message(STATUS "Waiting for feedback loop phase to complete...")
        return()
    endif()
    
    message(STATUS "Running completion phase...")
    
    # Execute completion agent
    execute_process(
        COMMAND ${CMAKE_BINARY_DIR}/completion_agent/completion_agent
        RESULT_VARIABLE completion_result
    )
    
    if(completion_result EQUAL 0)
        file(WRITE "${REDLINE_CACHE_DIR}/work_queue/completion/complete" "")
        message(STATUS "Task completed successfully")
    else()
        message(FATAL_ERROR "Completion agent failed with error ${completion_result}")
    endif()
endfunction()

# Function to verify all phases completed
function(verify_process_complete)
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/cognitive_agent/complete")
        message(FATAL_ERROR "Process not complete - cognitive phase missing")
        return()
    endif()

    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/planning/complete")
        message(FATAL_ERROR "Process not complete - planning phase missing")
        return()
    endif()
    
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/action_execution/complete")
        message(FATAL_ERROR "Process not complete - action execution phase missing")
        return()
    endif()
    
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/feedback/complete")
        message(FATAL_ERROR "Process not complete - feedback phase missing")
        return()
    endif()
    
    if(NOT EXISTS "${REDLINE_CACHE_DIR}/work_queue/completion/complete")
        message(FATAL_ERROR "Process not complete - completion phase missing")
        return()
    endif()
    
    message(STATUS "All phases completed successfully")
endfunction()
