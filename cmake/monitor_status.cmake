# Status monitoring implementation
# Provides real-time status updates for agents and operations

include(${CMAKE_CURRENT_LIST_DIR}/utils.cmake)

# Read status configuration
file(READ ${STATUS_CONFIG} STATUS_CONFIG_CONTENT)
string(JSON CONFIG_ROOT GET ${STATUS_CONFIG_CONTENT})

# Function to update status display
function(update_status_display)
    # Read current agent states
    get_property(AGENT_STATES GLOBAL PROPERTY AGENT_STATES)
    
    # Read progress log
    file(READ ${CMAKE_BINARY_DIR}/agent_progress.log PROGRESS_LOG)
    
    # Generate status report
    set(STATUS_REPORT "=== Redline System Status ===\n\n")
    
    # Agent Status Section
    string(APPEND STATUS_REPORT "Agent Status:\n")
    foreach(AGENT_STATE ${AGENT_STATES})
        string(REGEX MATCH "([^:]+):([^:]+)" MATCH ${AGENT_STATE})
        set(AGENT_NAME ${CMAKE_MATCH_1})
        set(AGENT_ROLE ${CMAKE_MATCH_2})
        string(APPEND STATUS_REPORT "  ${AGENT_NAME} (${AGENT_ROLE}): ACTIVE\n")
    endforeach()
    
    # Recent Progress Section
    string(APPEND STATUS_REPORT "\nRecent Progress:\n")
    string(REGEX MATCHALL "\[([^\]]+)\] ([^\n]+)" PROGRESS_ENTRIES "${PROGRESS_LOG}")
    list(REVERSE PROGRESS_ENTRIES)
    list(SUBLIST PROGRESS_ENTRIES 0 5 RECENT_ENTRIES)
    foreach(ENTRY ${RECENT_ENTRIES})
        string(APPEND STATUS_REPORT "  ${ENTRY}\n")
    endforeach()
    
    # Sandbox Status Section
    string(APPEND STATUS_REPORT "\nSandbox Status:\n")
    file(GLOB SANDBOX_DIRS "${CMAKE_BINARY_DIR}/sandboxes/*")
    foreach(SANDBOX ${SANDBOX_DIRS})
        get_filename_component(SANDBOX_NAME ${SANDBOX} NAME)
        string(APPEND STATUS_REPORT "  ${SANDBOX_NAME}: READY\n")
    endforeach()
    
    # Write status report
    file(WRITE ${CMAKE_BINARY_DIR}/status_report.txt ${STATUS_REPORT})
    
    # Update terminal display (if running in terminal)
    if(DEFINED ENV{TERM})
        execute_process(
            COMMAND clear
            COMMAND cat ${CMAKE_BINARY_DIR}/status_report.txt
        )
    endif()
endfunction()

# Main monitoring loop
while(TRUE)
    update_status_display()
    execute_process(COMMAND ${CMAKE_COMMAND} -E sleep 1)
endwhile()