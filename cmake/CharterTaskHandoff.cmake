function(charter_task_handoff TASK_DESCRIPTION)
    # 8B09616B-1495-4070-AC50-F52D72E34238
    # Propagate debug flags
    if(DEFINED DEBUG_SEND)
        set(DEBUG_SEND_FLAG "-DDEBUG_SEND=1")
        message(STATUS "Debug mode enabled (SEND)")
        message(STATUS "Processing task: ${TASK_DESCRIPTION}")
    endif()
    if(DEFINED DEBUG_RECEIVE)
        set(DEBUG_RECEIVE_FLAG "-DDEBUG_RECEIVE=1")
    endif()

    # Initial task processing
    set(PROMPT "Process this task through the Charter system: ${TASK_DESCRIPTION}")
    execute_llm("${PROMPT}" INITIAL_RESPONSE ${DEBUG_SEND_FLAG} ${DEBUG_RECEIVE_FLAG})
    
    # Agent handoff loop
    set(CURRENT_RESPONSE "${INITIAL_RESPONSE}")
    while(CURRENT_RESPONSE MATCHES "NEXT_AGENT:")
        # Extract next agent information
        string(REGEX MATCH "NEXT_AGENT:([a-zA-Z0-9_]+)" MATCH_AGENT "${CURRENT_RESPONSE}")
        string(REGEX REPLACE "NEXT_AGENT:([a-zA-Z0-9_]+)" "\\1" NEXT_AGENT "${MATCH_AGENT}")
        
        # Process with next agent
        set(AGENT_PROMPT "Agent ${NEXT_AGENT}, please process: ${CURRENT_RESPONSE}")
        execute_llm("${AGENT_PROMPT}" CURRENT_RESPONSE ${DEBUG_SEND_FLAG} ${DEBUG_RECEIVE_FLAG})
        
        # Apply any code edits
        if(CURRENT_RESPONSE MATCHES "FILE_EDIT:")
            llm_edit_code_by_coordinates("${CMAKE_SOURCE_DIR}/src/main.cpp")
        endif()
    endwhile()
    
    # Final task completion
    message(STATUS "Task completed with final response: ${CURRENT_RESPONSE}")
endfunction()
