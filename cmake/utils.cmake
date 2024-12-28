# Common utility functions for CMake modules

# Function to safely read JSON files
function(read_json_file FILENAME OUTPUT_VAR)
    if(NOT EXISTS "${FILENAME}")
        message(FATAL_ERROR "JSON file not found: ${FILENAME}")
    endif()
    
    file(READ "${FILENAME}" CONTENT)
    set(${OUTPUT_VAR} "${CONTENT}" PARENT_SCOPE)
endfunction()

# Function to ensure directory exists with proper permissions
function(ensure_directory DIR)
    if(NOT EXISTS "${DIR}")
        file(MAKE_DIRECTORY "${DIR}")
        execute_process(
            COMMAND chmod 755 "${DIR}"
            RESULT_VARIABLE CHMOD_RESULT
        )
        if(NOT CHMOD_RESULT EQUAL 0)
            message(WARNING "Failed to set permissions on ${DIR}")
        endif()
    endif()
endfunction()

# Function to log messages with timestamps
function(log_message MESSAGE LOG_FILE)
    string(TIMESTAMP TIMESTAMP "%Y-%m-%d %H:%M:%S")
    file(APPEND "${LOG_FILE}" "[${TIMESTAMP}] ${MESSAGE}\n")
endfunction()

# Function to validate agent state
function(validate_agent_state AGENT_NAME)
    get_property(AGENT_STATES GLOBAL PROPERTY AGENT_STATES)
    list(FIND AGENT_STATES "${AGENT_NAME}" AGENT_INDEX)
    if(AGENT_INDEX EQUAL -1)
        message(FATAL_ERROR "Invalid agent state: ${AGENT_NAME}")
    endif()
endfunction()

# Function to check if operation is idempotent
function(check_idempotent OPERATION_NAME RESULT_VAR)
    if(DEFINED OPERATION_${OPERATION_NAME}_COMPLETE)
        set(${RESULT_VAR} TRUE PARENT_SCOPE)
    else()
        set(${RESULT_VAR} FALSE PARENT_SCOPE)
    endif()
endfunction()

# Function to manage sandbox state
function(manage_sandbox_state SANDBOX_NAME STATE)
    set(SANDBOX_STATE_FILE "${CMAKE_BINARY_DIR}/sandboxes/${SANDBOX_NAME}/state.txt")
    file(WRITE "${SANDBOX_STATE_FILE}" "${STATE}")
endfunction()

# Function to get agent home directory
function(get_agent_home AGENT_NAME AGENT_ROLE OUTPUT_VAR)
    set(AGENT_HOME "$ENV{HOME}/.local/cache/redline/${AGENT_ROLE}/${AGENT_NAME}")
    set(${OUTPUT_VAR} "${AGENT_HOME}" PARENT_SCOPE)
endfunction()

# Function to parse version string
function(parse_version VERSION_STRING)
    string(REGEX MATCH "^([0-9]+)\\.([0-9]+)\\.([0-9]+)" VERSION_MATCH "${VERSION_STRING}")
    if(VERSION_MATCH)
        set(VERSION_MAJOR "${CMAKE_MATCH_1}" PARENT_SCOPE)
        set(VERSION_MINOR "${CMAKE_MATCH_2}" PARENT_SCOPE)
        set(VERSION_PATCH "${CMAKE_MATCH_3}" PARENT_SCOPE)
    else()
        message(FATAL_ERROR "Invalid version string: ${VERSION_STRING}")
    endif()
endfunction()

# Function to check system requirements
function(check_system_requirements)
    # Check for required programs
    find_program(CHMOD_PROGRAM chmod)
    if(NOT CHMOD_PROGRAM)
        message(FATAL_ERROR "chmod not found")
    endif()
    
    # Check for required environment variables
    if(NOT DEFINED ENV{HOME})
        message(FATAL_ERROR "HOME environment variable not set")
    endif()
    
    # Check for minimum CMake version
    if(CMAKE_VERSION VERSION_LESS 3.15)
        message(FATAL_ERROR "CMake 3.15 or higher required")
    endif()
endfunction()

# Function to generate unique identifier
function(generate_uuid OUTPUT_VAR)
    string(RANDOM LENGTH 32 ALPHABET "0123456789abcdef" UUID)
    set(${OUTPUT_VAR} "${UUID}" PARENT_SCOPE)
endfunction()

# Function to sanitize file paths
function(sanitize_path PATH OUTPUT_VAR)
    string(REGEX REPLACE "[^a-zA-Z0-9_/.-]" "_" SANITIZED "${PATH}")
    set(${OUTPUT_VAR} "${SANITIZED}" PARENT_SCOPE)
endfunction()

# Initialize common variables
if(NOT DEFINED REDLINE_INITIALIZED)
    set(REDLINE_INITIALIZED TRUE)
    set(REDLINE_CACHE_DIR "$ENV{HOME}/.local/cache/redline")
    set(REDLINE_LOG_DIR "${CMAKE_BINARY_DIR}/logs")
    ensure_directory("${REDLINE_CACHE_DIR}")
    ensure_directory("${REDLINE_LOG_DIR}")
endif()