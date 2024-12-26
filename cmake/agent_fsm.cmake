# Agent Finite State Machine implementation
# Manages state transitions and rules for the agent system

include(${CMAKE_CURRENT_LIST_DIR}/utils.cmake)

# Agent States
set(AGENT_STATE_INIT "init")
set(AGENT_STATE_COGNITIVE "cognitive_analysis")
set(AGENT_STATE_PLANNING "planning")
set(AGENT_STATE_EXECUTION "execution")
set(AGENT_STATE_FEEDBACK "feedback")
set(AGENT_STATE_COMPLETION "completion")
set(AGENT_STATE_ERROR "error")

# Function to validate state transition
function(validate_transition FROM_STATE TO_STATE RESULT_VAR)
    set(TRANSITION "${FROM_STATE}:${TO_STATE}")
    set(VALID_TRANSITIONS
        "init:cognitive_analysis"
        "cognitive_analysis:planning"
        "planning:execution"
        "execution:feedback"
        "feedback:cognitive_analysis"
        "feedback:completion"
        "completion:init"
        "*:error"
        "error:init"
    )
    # ... validation logic
endfunction()

# Function to get current agent state
function(get_agent_state AGENT_NAME OUTPUT_VAR)
    set(STATE_FILE "${CMAKE_BINARY_DIR}/states/${AGENT_NAME}.state")
    if(EXISTS "${STATE_FILE}")
        file(READ "${STATE_FILE}" CURRENT_STATE)
        string(STRIP "${CURRENT_STATE}" CURRENT_STATE)
    else()
        set(CURRENT_STATE "${AGENT_STATE_INIT}")
    endif()
    set(${OUTPUT_VAR} "${CURRENT_STATE}" PARENT_SCOPE)
endfunction()

# Function to set agent state
function(set_agent_state AGENT_NAME NEW_STATE)
    get_agent_state(${AGENT_NAME} CURRENT_STATE)
    validate_transition("${CURRENT_STATE}" "${NEW_STATE}" IS_VALID)
    
    if(NOT IS_VALID)
        message(FATAL_ERROR "Invalid state transition: ${CURRENT_STATE} -> ${NEW_STATE}")
    endif()
    
    set(STATE_FILE "${CMAKE_BINARY_DIR}/states/${AGENT_NAME}.state")
    file(WRITE "${STATE_FILE}" "${NEW_STATE}")
    
    # Log transition
    log_message("Agent ${AGENT_NAME} transitioned: ${CURRENT_STATE} -> ${NEW_STATE}" 
               "${CMAKE_BINARY_DIR}/logs/state_transitions.log")
endfunction()

# Function to check if agent is in specific state
function(is_agent_in_state AGENT_NAME STATE RESULT_VAR)
    get_agent_state(${AGENT_NAME} CURRENT_STATE)
    if("${CURRENT_STATE}" STREQUAL "${STATE}")
        set(${RESULT_VAR} TRUE PARENT_SCOPE)
    else()
        set(${RESULT_VAR} FALSE PARENT_SCOPE)
    endif()
endfunction()

# Function to execute state-specific actions
function(execute_state_actions AGENT_NAME)
    get_agent_state(${AGENT_NAME} CURRENT_STATE)
    
    # State-specific actions
    if("${CURRENT_STATE}" STREQUAL "${AGENT_STATE_COGNITIVE}")
        execute_cognitive_analysis(${AGENT_NAME})
    elseif("${CURRENT_STATE}" STREQUAL "${AGENT_STATE_PLANNING}")
        execute_planning_phase(${AGENT_NAME})
    elseif("${CURRENT_STATE}" STREQUAL "${AGENT_STATE_EXECUTION}")
        execute_action_phase(${AGENT_NAME})
    elseif("${CURRENT_STATE}" STREQUAL "${AGENT_STATE_FEEDBACK}")
        execute_feedback_loop(${AGENT_NAME})
    elseif("${CURRENT_STATE}" STREQUAL "${AGENT_STATE_COMPLETION}")
        execute_completion_check(${AGENT_NAME})
    endif()
endfunction()

# State-specific execution functions
function(execute_cognitive_analysis AGENT_NAME)
    # Load agent's charter fragments
    set(CHARTER_FILE "${CMAKE_BINARY_DIR}/agents/${AGENT_NAME}/charter_fragments.txt")
    if(EXISTS "${CHARTER_FILE}")
        file(READ "${CHARTER_FILE}" CHARTER_CONTENT)
    endif()
    
    # Execute cognitive analysis
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            AGENT_NAME=${AGENT_NAME}
            CHARTER_CONTENT=${CHARTER_CONTENT}
            ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/cognitive_analysis.py
        RESULT_VARIABLE ANALYSIS_RESULT
    )
    
    if(NOT ANALYSIS_RESULT EQUAL 0)
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_ERROR}")
    else()
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_PLANNING}")
    endif()
endfunction()

function(execute_planning_phase AGENT_NAME)
    # Load cognitive analysis results
    set(ANALYSIS_FILE "${CMAKE_BINARY_DIR}/agents/${AGENT_NAME}/analysis_results.json")
    if(EXISTS "${ANALYSIS_FILE}")
        file(READ "${ANALYSIS_FILE}" ANALYSIS_CONTENT)
    endif()
    
    # Execute planning
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            AGENT_NAME=${AGENT_NAME}
            ANALYSIS_CONTENT=${ANALYSIS_CONTENT}
            ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/planning_phase.py
        RESULT_VARIABLE PLANNING_RESULT
    )
    
    if(NOT PLANNING_RESULT EQUAL 0)
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_ERROR}")
    else()
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_EXECUTION}")
    endif()
endfunction()

function(execute_action_phase AGENT_NAME)
    # Load plan
    set(PLAN_FILE "${CMAKE_BINARY_DIR}/agents/${AGENT_NAME}/plan.json")
    if(EXISTS "${PLAN_FILE}")
        file(READ "${PLAN_FILE}" PLAN_CONTENT)
    endif()
    
    # Execute actions
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            AGENT_NAME=${AGENT_NAME}
            PLAN_CONTENT=${PLAN_CONTENT}
            ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/action_execution.py
        RESULT_VARIABLE ACTION_RESULT
    )
    
    if(NOT ACTION_RESULT EQUAL 0)
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_ERROR}")
    else()
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_FEEDBACK}")
    endif()
endfunction()

function(execute_feedback_loop AGENT_NAME)
    # Load execution results
    set(RESULTS_FILE "${CMAKE_BINARY_DIR}/agents/${AGENT_NAME}/execution_results.json")
    if(EXISTS "${RESULTS_FILE}")
        file(READ "${RESULTS_FILE}" RESULTS_CONTENT)
    endif()
    
    # Execute feedback analysis
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            AGENT_NAME=${AGENT_NAME}
            RESULTS_CONTENT=${RESULTS_CONTENT}
            ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/feedback_analysis.py
        RESULT_VARIABLE FEEDBACK_RESULT
        OUTPUT_VARIABLE FEEDBACK_OUTPUT
    )
    
    if(NOT FEEDBACK_RESULT EQUAL 0)
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_ERROR}")
    else()
        # Parse feedback decision
        if("${FEEDBACK_OUTPUT}" MATCHES "NEEDS_REVISION")
            set_agent_state(${AGENT_NAME} "${AGENT_STATE_COGNITIVE}")
        elseif("${FEEDBACK_OUTPUT}" MATCHES "COMPLETE")
            set_agent_state(${AGENT_NAME} "${AGENT_STATE_COMPLETION}")
        else()
            set_agent_state(${AGENT_NAME} "${AGENT_STATE_PLANNING}")
        endif()
    endif()
endfunction()

function(execute_completion_check AGENT_NAME)
    # Load all results
    set(RESULTS_DIR "${CMAKE_BINARY_DIR}/agents/${AGENT_NAME}")
    
    # Execute completion verification
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            AGENT_NAME=${AGENT_NAME}
            RESULTS_DIR=${RESULTS_DIR}
            ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/completion_check.py
        RESULT_VARIABLE CHECK_RESULT
    )
    
    if(NOT CHECK_RESULT EQUAL 0)
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_ERROR}")
    else()
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_INIT}")
    endif()
endfunction()

# Initialize FSM system
function(initialize_fsm_system)
    # Create necessary directories
    file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/states")
    file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/logs")
    
    # Initialize all agents to init state
    get_property(AGENT_STATES GLOBAL PROPERTY AGENT_STATES)
    foreach(AGENT_STATE ${AGENT_STATES})
        string(REGEX MATCH "([^:]+)" AGENT_NAME ${AGENT_STATE})
        set_agent_state(${AGENT_NAME} "${AGENT_STATE_INIT}")
    endforeach()
    
    message(STATUS "FSM system initialized")
endfunction()