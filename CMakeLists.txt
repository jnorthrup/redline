cmake_minimum_required(VERSION 3.10)
project(redline)

# Create base directory
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ~/.local/redline)

# Create role-based directories
set(ROLES
    "action_execution_agent"
    "cognitive_agent"
    "completion_agent"
    "feedback_loop_agent"
    "planning_agent"
)

foreach(role IN LISTS ROLES)
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ~/.local/redline/${role})
    execute_process(COMMAND chmod 750 ~/.local/redline/${role})
endforeach()

# Create CMake cache directory
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ~/.local/redline/cmake_cache)
execute_process(COMMAND chmod 770 ~/.local/redline/cmake_cache)

# Function to setup role-specific environment
function(setup_environment role_name)
    set(ROLE_DIR ~/.local/redline/${role_name})
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${ROLE_DIR}/work)
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${ROLE_DIR}/cache)
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${ROLE_DIR}/logs)
    execute_process(COMMAND chmod 750 ${ROLE_DIR}/work)
    execute_process(COMMAND chmod 750 ${ROLE_DIR}/cache)
    execute_process(COMMAND chmod 750 ${ROLE_DIR}/logs)
endfunction()

# Function to handle CMake integration
function(handle_cmake_handoff role_name)
    set(ROLE_DIR ~/.local/redline/${role_name})
    set(CMAKE_CACHE_DIR ~/.local/redline/cmake_cache)
    execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink ${CMAKE_CACHE_DIR} ${ROLE_DIR}/cache/cmake)
endfunction()

# Function to analyze CMake cache files
function(analyze_cmake_cache)
    set(CMAKE_CACHE_FILES
        "action_execution_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "cognitive_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "completion_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "feedback_loop_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "planning_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
    )

    set(processed 0)
    foreach(file IN LISTS CMAKE_CACHE_FILES)
        if(NOT EXISTS ${file})
            message(WARNING "File not found - ${file}")
            continue
        endif()

        message(STATUS "----------------------------------------")
        message(STATUS "File: ${file}")
        message(STATUS "----------------------------------------")

        file(STRINGS ${file} file_content NEWLINE_CONSUME)
        foreach(line IN LISTS file_content)
            if(line MATCHES "CMAKE_RELATIVE_PATH_TOP_SOURCE")
                string(REGEX REPLACE ".*CMAKE_RELATIVE_PATH_TOP_SOURCE:STATIC=(.*)$" "\\1" source_path ${line})
                message(STATUS "CMAKE_RELATIVE_PATH_TOP_SOURCE: ${source_path}")
            endif()

            if(line MATCHES "CMAKE_RELATIVE_PATH_TOP_BINARY")
                string(REGEX REPLACE ".*CMAKE_RELATIVE_PATH_TOP_BINARY:STATIC=(.*)$" "\\1" binary_path ${line})
                message(STATUS "CMAKE_RELATIVE_PATH_TOP_BINARY: ${binary_path}")
            endif()
        endforeach()

        math(EXPR processed "${processed} + 1")
    endforeach()

    message(STATUS "----------------------------------------")
    message(STATUS "Analysis complete. Processed ${processed} files.")
endfunction()

# Function to query Perplexity AI
function(query_perplexity prompt)
    set(PERPLEXITY_API $ENV{PERPLEXITY_API})
    if(NOT PERPLEXITY_API)
        message(FATAL_ERROR "Error: PERPLEXITY_API environment variable is not set.")
    endif()

    set(json_request "{\"model\": \"pplx-7b-online\", \"messages\": [{ \"role\": \"system\", \"content\": \"Be precise and concise.\" }, { \"role\": \"user\", \"content\": \"${prompt}\" }], \"stream\": false}")
    execute_process(
        COMMAND curl --silent --request POST --url https://api.perplexity.ai/chat/completions --header "accept: application/json" --header "authorization: Bearer ${PERPLEXITY_API}" --header "content-type: application/json" --data "${json_request}"
        OUTPUT_VARIABLE response
    )
    message(STATUS "Perplexity AI Response: ${response}")
endfunction()

# Function to query GROK
function(query_groq prompt)
    set(GROQ_API_KEY $ENV{GROQ_API_KEY})
    if(NOT GROQ_API_KEY)
        message(FATAL_ERROR "Error: GROQ_API_KEY environment variable is not set.")
    endif()

    set(json_request "{\"model\": \"mixtral-8x7b-32768\", \"messages\": [{ \"role\": \"user\", \"content\": \"${prompt}\" }], \"temperature\": 0.5, \"max_tokens\": 1024}")
    execute_process(
        COMMAND curl --silent --request POST --url https://api.groq.com/openai/v1/chat/completions --header "accept: application/json" --header "authorization: Bearer ${GROQ_API_KEY}" --header "content-type: application/json" --data "${json_request}"
        OUTPUT_VARIABLE response
    )
    message(STATUS "GROK Response: ${response}")
endfunction()

# Function to initialize memory
function(init_memory)
    set(MEMORY_FILE ~/.local/redline/work_queue/memory.txt)
    if(NOT EXISTS ${MEMORY_FILE})
        file(WRITE ${MEMORY_FILE} "{}")
    endif()
endfunction()

# Function to read the charter and task details
function(read_charter_and_task)
    set(CHARTER_FILE CHARTER.MD)
    if(NOT EXISTS ${CHARTER_FILE})
        message(FATAL_ERROR "Error: ${CHARTER_FILE} not found.")
    endif()

    file(READ ${CHARTER_FILE} CHARTER_CONTENT)
    message(STATUS "Charter content read successfully.")
    set(CHARTER_CONTENT ${CHARTER_CONTENT} PARENT_SCOPE)
endfunction()

# Function to generate cognitive agent prompt
function(cognitive_agent_prompt task)
    set(RECEIVER_ROLE "system")
    set(SENDER_ROLE "user")
    set(SENDER_PROMPT "You are the Cognitive Agent responsible for initial reasoning and understanding. Based on the following charter and task, please: 1. Generate a detailed explanation of the challenge 2. Identify any information gaps or uncertainties 3. Provide key findings and insights for planning. Charter: ${CHARTER_CONTENT} Task: ${task} Current Memory: $(cat ${MEMORY_FILE}) Please structure your response as JSON with the following fields: { \"explanation\": \"detailed problem explanation\", \"gaps\": [\"list of identified gaps\"], \"findings\": [\"key insights and findings\"], \"confidence\": 0-1 score }")
    set(SENDER_PROMPT ${SENDER_PROMPT} PARENT_SCOPE)
endfunction()

# Function to generate planning agent prompt
function(planning_agent_prompt cognitive_response)
    set(RECEIVER_ROLE "system")
    set(SENDER_ROLE "user")
    set(SENDER_PROMPT "You are the Planning Agent responsible for creating a detailed execution plan. Based on the cognitive analysis and current state, please create a structured plan. Cognitive Analysis: ${cognitive_response} Current Memory: $(cat ${MEMORY_FILE}) Please structure your response as JSON with the following fields: { \"steps\": [ { \"id\": \"step identifier\", \"description\": \"step description\", \"commands\": [\"list of commands to execute\"], \"expected_outcomes\": [\"expected results\"], \"validation_criteria\": [\"how to validate success\"] } ], \"dependencies\": [\"step dependencies\"], \"estimated_completion_time\": \"time estimate\" }")
    set(SENDER_PROMPT ${SENDER_PROMPT} PARENT_SCOPE)
endfunction()

# Function to generate action execution agent prompt
function(action_execution_agent_prompt plan current_step)
    set(RECEIVER_ROLE "system")
    set(SENDER_ROLE "user")
    set(SENDER_PROMPT "You are the Action Execution Agent responsible for executing commands and collecting observations. Please execute the following step and analyze its results. Current Plan: ${plan} Current Step: ${current_step} Current Memory: $(cat ${MEMORY_FILE}) Please structure your response as JSON with the following fields: { \"executed_commands\": [\"commands that were run\"], \"observations\": [\"observed outputs and results\"], \"success\": boolean, \"error_details\": \"error information if any\", \"artifacts_generated\": [\"list of generated artifacts\"] }")
    set(SENDER_PROMPT ${SENDER_PROMPT} PARENT_SCOPE)
endfunction()

# Function to generate feedback loop agent prompt
function(feedback_loop_agent_prompt action_results original_plan)
    set(RECEIVER_ROLE "system")
    set(SENDER_ROLE "user")
    set(SENDER_PROMPT "You are the Feedback Loop Agent responsible for evaluating results and determining next steps. Please analyze the latest action results and provide feedback. Action Results: ${action_results} Original Plan: ${original_plan} Current Memory: $(cat ${MEMORY_FILE}) Please structure your response as JSON with the following fields: { \"success_criteria_met\": boolean, \"observations_analysis\": \"analysis of results\", \"plan_adjustments\": [\"needed adjustments to plan\"], \"next_step\": \"next step to take\", \"memory_updates\": [\"updates to make to memory\"], \"continue_iteration\": boolean }")
    set(SENDER_PROMPT ${SENDER_PROMPT} PARENT_SCOPE)
endfunction()

# Function to generate completion agent prompt
function(completion_agent_prompt full_history)
    set(RECEIVER_ROLE "system")
    set(SENDER_ROLE "user")
    set(SENDER_PROMPT "You are the Completion Agent responsible for final verification and delivery. Please verify that all requirements have been met. Execution History: ${full_history} Current Memory: $(cat ${MEMORY_FILE}) Please structure your response as JSON with the following fields: { \"requirements_met\": boolean, \"verification_details\": [\"verification steps performed\"], \"outstanding_issues\": [\"any remaining issues\"], \"final_artifacts\": [\"list of final deliverables\"], \"completion_status\": \"FINISH or CONTINUE\" }")
    set(SENDER_PROMPT ${SENDER_PROMPT} PARENT_SCOPE)
endfunction()

# Function to execute LLM API call
function(execute_llm prompt llm)
    set(LLM_API_URL "https://api.example.com/llm")
    if(llm STREQUAL "perplexity")
        set(LLM_API_URL "https://api.perplexity.ai/chat/completions")
        set(json_request "{\"model\": \"pplx-7b-online\", \"messages\": [{ \"role\": \"system\", \"content\": \"Be precise and concise.\" }, { \"role\": \"user\", \"content\": \"${prompt}\" }], \"stream\": false}")
    elseif(llm STREQUAL "grok")
        set(LLM_API_URL "https://api.groq.com/openai/v1/chat/completions")
        set(json_request "{\"model\": \"mixtral-8x7b-32768\", \"messages\": [{ \"role\": \"user\", \"content\": \"${prompt}\" }], \"temperature\": 0.5, \"max_tokens\": 1024}")
    else
        message(FATAL_ERROR "Error: Invalid LLM specified. Choose 'perplexity' or 'grok'.")
    endif()

    execute_process(
        COMMAND curl --silent --request POST --url ${LLM_API_URL} --header "accept: application/json" --header "authorization: Bearer $ENV{${llm}_API}" --header "content-type: application/json" --data "${json_request}"
        OUTPUT_VARIABLE response
    )
    message(STATUS "${llm} Response: ${response}")
endfunction()

# Function to update memory
function(update_memory updates)
    set(MEMORY_FILE ~/.local/redline/work_queue/memory.txt)
    file(READ ${MEMORY_FILE} CURRENT_MEMORY)
    # Merge updates with current memory (would need jq in practice)
    file(WRITE ${MEMORY_FILE} "${CURRENT_MEMORY}")
endfunction()

# Function to log observations
function(log_observation observation)
    set(OBSERVATION_FILE ~/.local/redline/work_queue/observations.txt)
    file(APPEND ${OBSERVATION_FILE} "$(date -u +\"%Y-%m-%dT%H:%M:%SZ\") - ${observation}\n")
endfunction()

# Function to run feedback loop
function(run_feedback_loop)
    set(FEEDBACK_LOOP_SCRIPT "prompt_feedback_loop.py")
    if(NOT EXISTS ${FEEDBACK_LOOP_SCRIPT})
        message(FATAL_ERROR "Error: ${FEEDBACK_LOOP_SCRIPT} not found.")
    endif()

    execute_process(
        COMMAND python3 ${FEEDBACK_LOOP_SCRIPT}
        OUTPUT_VARIABLE response
    )
    message(STATUS "Feedback Loop Response: ${response}")
endfunction()

# Main execution loop
function(main task)
    set(STATE_DIR ~/.local/redline/work_queue)
    set(OBSERVATION_FILE ${STATE_DIR}/observations.txt)
    set(MEMORY_FILE ${STATE_DIR}/memory.txt)

    # Ensure state directory exists
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${STATE_DIR})

    # Initialize or load memory
    init_memory

    # Read charter and task details
    read_charter_and_task

    set(ITERATION 0)
    set(CONTINUE true)

    while(CONTINUE AND ITERATION LESS 10)
        message(STATUS "Starting iteration ${ITERATION}...")

        # Cognitive analysis
        cognitive_agent_prompt("${task}")
        execute_llm("${SENDER_PROMPT}" "perplexity")
        set(COGNITIVE_RESPONSE ${response})

        # Planning
        planning_agent_prompt("${COGNITIVE_RESPONSE}")
        execute_llm("${SENDER_PROMPT}" "perplexity")
        set(PLAN_RESPONSE ${response})

        # Extract steps from plan and execute each one
        set(STEPS $(echo "${PLAN_RESPONSE}" | jq -r '.steps[]'))
        foreach(CURRENT_STEP IN LISTS STEPS)
            action_execution_agent_prompt("${PLAN_RESPONSE}" "${CURRENT_STEP}")
            execute_llm("${SENDER_PROMPT}" "perplexity")
            set(ACTION_RESPONSE ${response})

            # Feedback loop
            feedback_loop_agent_prompt("${ACTION_RESPONSE}" "${PLAN_RESPONSE}")
            execute_llm("${SENDER_PROMPT}" "perplexity")
            set(FEEDBACK_RESPONSE ${response})

            # Update memory based on feedback
            update_memory("${FEEDBACK_RESPONSE}")

            # Check completion
            completion_agent_prompt($(cat ${OBSERVATION_FILE}))
            execute_llm("${SENDER_PROMPT}" "perplexity")
            set(COMPLETION_RESPONSE ${response})

            if(COMPLETION_RESPONSE MATCHES "FINISH")
                set(CONTINUE false)
                message(STATUS "Task completed successfully.")
            endif()

            math(EXPR ITERATION "${ITERATION} + 1")
        endforeach()

        if(ITERATION GREATER_EQUAL 10)
            message(WARNING "Warning: Maximum iterations reached")
        endif()
    endwhile()
endfunction()

# Add subdirectories
add_subdirectory(action_execution_agent)
add_subdirectory(cognitive_agent)
add_subdirectory(completion_agent)
add_subdirectory(feedback_loop_agent)
add_subdirectory(planning_agent)
add_subdirectory(src)
add_subdirectory(test)
add_subdirectory(tools)
add_subdirectory(lmstudio)

# Setup environment for all roles
foreach(role IN LISTS ROLES)
    setup_environment(${role})
endforeach()

# Function to setup Redline environment
function(setup_redline_env)
    set(STATE_DIR ~/.local/redline)
    set(WORK_QUEUE_DIR ${STATE_DIR}/work_queue)
    set(CACHE_DIR ${STATE_DIR}/cache)

    # Ensure state directory exists
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${STATE_DIR})

    # Ensure work queue directory exists
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${WORK_QUEUE_DIR})
    execute_process(COMMAND chmod 750 ${WORK_QUEUE_DIR})

    # Ensure cache directory exists
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${CACHE_DIR})
    execute_process(COMMAND chmod 750 ${CACHE_DIR})

    # Setup environment for all roles
    foreach(role IN LISTS ROLES)
        setup_environment(${role})
    endforeach()
endfunction()

# Call the setup_redline_env function
setup_redline_env()

# Run the feedback loop
run_feedback_loop()
