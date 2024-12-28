# CMake functions for handling the prompt feedback loop

# Function to initialize memory
function(init_memory state_dir)
    set(MEMORY_PATH ${state_dir}/memory.json)
    if(NOT EXISTS ${MEMORY_PATH})
        file(WRITE ${MEMORY_PATH} "{}")
    endif()
endfunction()

# Function to log observations
function(log_observation state_dir observation)
    set(OBSERVATION_PATH ${state_dir}/observations.txt)
    file(APPEND ${OBSERVATION_PATH} "$(date -u +\"%Y-%m-%dT%H:%M:%SZ\") - ${observation}\n")
endfunction()

# Function to read the charter
function(read_charter)
    set(CHARTER_PATH CHARTER.MD)
    if(NOT EXISTS ${CHARTER_PATH})
        message(FATAL_ERROR "Error: ${CHARTER_PATH} not found.")
    endif()

    file(READ ${CHARTER_PATH} CHARTER_CONTENT)
    message(STATUS "Charter content read successfully.")
    set(CHARTER_CONTENT ${CHARTER_CONTENT} PARENT_SCOPE)
endfunction()

# Function to execute LLM API call
function(execute_llm prompt llm llm_response)
    # Set API key environment variable based on LLM choice
    if(llm STREQUAL "perplexity")
        set(ENV{PERPLEXITY_API} "$ENV{PERPLEXITY_API}")
        unset(ENV{GROQ_API_KEY})
    elseif(llm STREQUAL "grok")
        set(ENV{GROQ_API_KEY} "$ENV{GROQ_API_KEY}")
        unset(ENV{PERPLEXITY_API})
    else
        message(FATAL_ERROR "Error: Invalid LLM specified. Choose 'perplexity' or 'grok'.")
    endif()
    
    set(ENV{AgentIdentity} "$ENV{AgentIdentity}")
    set(ENV{AgentRoles} "$ENV{AgentRoles}")

    # Get the calling function name to set agent identity
    get_function_call_stack(CALL_STACK)
    list(GET CALL_STACK 1 CALLER_FUNCTION)
    if(CALLER_FUNCTION MATCHES "cognitive_analysis")
        set(ENV{AgentIdentity} "Cognitive Agent")
        set(ENV{AgentRoles} "initial reasoning and understanding")
    elseif(CALLER_FUNCTION MATCHES "create_plan")
        set(ENV{AgentIdentity} "Planning Agent")
        set(ENV{AgentRoles} "creating detailed execution plans")
    elseif(CALLER_FUNCTION MATCHES "execute_step")
        set(ENV{AgentIdentity} "Action Execution Agent")
        set(ENV{AgentRoles} "executing commands and collecting observations")
    elseif(CALLER_FUNCTION MATCHES "evaluate_feedback")
        set(ENV{AgentIdentity} "Feedback Loop Agent")
        set(ENV{AgentRoles} "evaluating results and determining next steps")
    elseif(CALLER_FUNCTION MATCHES "verify_completion")
        set(ENV{AgentIdentity} "Completion Agent")
        set(ENV{AgentRoles} "final verification and delivery")
    endif()

    execute_process(
        COMMAND ./llm_api_call "${prompt}"
        OUTPUT_VARIABLE llm_response
        RESULT_VARIABLE llm_result
    )

    if(NOT llm_result EQUAL 0)
        message(FATAL_ERROR "Error: LLM API call failed with exit code ${llm_result}")
    endif()

    # Read response from file since llm_api_call writes to llm_response.txt
    file(READ llm_response.txt llm_response)
    message(STATUS "${llm} Response: ${llm_response}")
    set(llm_response ${llm_response} PARENT_SCOPE)
endfunction()

# Function to perform cognitive analysis
function(cognitive_analysis task state_dir)
    read_charter()
    set(MEMORY_PATH ${state_dir}/memory.json)
    file(READ ${MEMORY_PATH} MEMORY_CONTENT)
    
    set(prompt "You are the Cognitive Agent responsible for initial reasoning and understanding.
Based on the following charter and task, please:
1. Generate a detailed explanation of the challenge
2. Identify any information gaps or uncertainties
3. Provide key findings and insights for planning

Charter:
${CHARTER_CONTENT}

Task:
${task}

Current Memory:
${MEMORY_CONTENT}

Please structure your response as JSON with the following fields:
{
    \"explanation\": \"detailed problem explanation\",
    \"gaps\": [\"list of identified gaps\"],
    \"findings\": [\"key insights and findings\"],
    \"confidence\": 0-1 score
}")
    
    execute_llm("${prompt}" "perplexity")
    log_observation(${state_dir} "Cognitive Analysis: ${llm_response}")
    set(llm_response ${llm_response} PARENT_SCOPE)
endfunction()

# Function to create a plan
function(create_plan cognitive_result state_dir)
    set(MEMORY_PATH ${state_dir}/memory.json)
    file(READ ${MEMORY_PATH} MEMORY_CONTENT)
    
    set(prompt "You are the Planning Agent responsible for creating a detailed execution plan.
Based on the cognitive analysis and current state, please create a structured plan.

Cognitive Analysis:
${cognitive_result}

Current Memory:
${MEMORY_CONTENT}

Please structure your response as JSON with the following fields:
{
    \"steps\": [
        {
            \"id\": \"step identifier\",
            \"description\": \"step description\",
            \"commands\": [\"list of commands to execute\"],
            \"expected_outcomes\": [\"expected results\"],
            \"validation_criteria\": [\"how to validate success\"]
        }
    ],
    \"dependencies\": [\"step dependencies\"],
    \"estimated_completion_time\": \"time estimate\"
}")
    
    execute_llm("${prompt}" "perplexity")
    log_observation(${state_dir} "Plan: ${llm_response}")
    set(llm_response ${llm_response} PARENT_SCOPE)
endfunction()

# Function to execute a step
function(execute_step plan_result step_data state_dir)
    set(MEMORY_PATH ${state_dir}/memory.json)
    file(READ ${MEMORY_PATH} MEMORY_CONTENT)
    
    set(prompt "You are the Action Execution Agent responsible for executing commands and collecting observations.
Please execute the following step and analyze its results.

Current Plan:
${plan_result}

Current Step:
${step_data}

Current Memory:
${MEMORY_CONTENT}

Please structure your response as JSON with the following fields:
{
    \"executed_commands\": [\"commands that were run\"],
    \"observations\": [\"observed outputs and results\"],
    \"success\": boolean,
    \"error_details\": \"error information if any\",
    \"artifacts_generated\": [\"list of generated artifacts\"]
}")
    
    execute_llm("${prompt}" "perplexity")
    log_observation(${state_dir} "Action Results: ${llm_response}")
    set(llm_response ${llm_response} PARENT_SCOPE)
endfunction()

# Function to evaluate feedback
function(evaluate_feedback action_result plan_result state_dir)
    set(MEMORY_PATH ${state_dir}/memory.json)
    file(READ ${MEMORY_PATH} MEMORY_CONTENT)
    
    set(prompt "You are the Feedback Loop Agent responsible for evaluating results and determining next steps.
Please analyze the latest action results and provide feedback.

Action Results:
${action_result}

Original Plan:
${plan_result}

Current Memory:
${MEMORY_CONTENT}

Please structure your response as JSON with the following fields:
{
    \"success_criteria_met\": boolean,
    \"observations_analysis\": \"analysis of results\",
    \"plan_adjustments\": [\"needed adjustments to plan\"],
    \"next_step\": \"next step to take\",
    \"memory_updates\": [\"updates to make to memory\"],
    \"continue_iteration\": boolean
}")
    
    execute_llm("${prompt}" "perplexity")
    log_observation(${state_dir} "Feedback: ${llm_response}")
    set(llm_response ${llm_response} PARENT_SCOPE)
endfunction()

# Function to verify completion
function(verify_completion execution_history state_dir)
    set(MEMORY_PATH ${state_dir}/memory.json)
    file(READ ${MEMORY_PATH} MEMORY_CONTENT)
    
    set(prompt "You are the Completion Agent responsible for final verification and delivery.
Based on the execution history and current state, please verify that all requirements have been met.

Execution History:
${execution_history}

Current Memory:
${MEMORY_CONTENT}

Please structure your response as JSON with the following fields:
{
    \"requirements_met\": boolean,
    \"verification_details\": [\"verification steps performed\"],
    \"outstanding_issues\": [\"any remaining issues\"],
    \"final_artifacts\": [\"list of final deliverables\"],
    \"completion_status\": \"FINISH or CONTINUE\"
}")
    
    execute_llm("${prompt}" "perplexity")
    log_observation(${state_dir} "Completion Verification: ${llm_response}")
    set(llm_response ${llm_response} PARENT_SCOPE)
endfunction()

# Main function to run the feedback loop
function(run_feedback_loop task state_dir)
    init_memory(${state_dir})
    read_charter()
    
    set(ITERATION_COUNT 0)
    set(SHOULD_CONTINUE true)
    
    while(SHOULD_CONTINUE AND ITERATION_COUNT LESS 10)
        message(STATUS "Starting iteration ${ITERATION_COUNT}...")
        
        # Cognitive analysis
        cognitive_analysis("${task}" ${state_dir})
        set(COGNITIVE_RESULT ${llm_response})
        
        # Planning
        create_plan("${COGNITIVE_RESULT}" ${state_dir})
        set(PLAN_RESULT ${llm_response})
        
        # Extract steps from plan using CMake string manipulation
        string(JSON STEPS_COUNT LENGTH "${PLAN_RESULT}" "steps")
        math(EXPR STEPS_MAX "${STEPS_COUNT} - 1")
        
        foreach(STEP_INDEX RANGE ${STEPS_MAX})
            string(JSON CURRENT_STEP GET "${PLAN_RESULT}" "steps" ${STEP_INDEX})
            
            # Execute step
            execute_step("${PLAN_RESULT}" "${CURRENT_STEP}" ${state_dir})
            set(ACTION_RESULT ${llm_response})
            
            # Evaluate feedback
            evaluate_feedback("${ACTION_RESULT}" "${PLAN_RESULT}" ${state_dir})
            set(FEEDBACK_RESULT ${llm_response})
            
            # Update memory based on feedback using CMake string manipulation
            string(JSON MEMORY_UPDATES_COUNT LENGTH "${FEEDBACK_RESULT}" "memory_updates")
            math(EXPR UPDATES_MAX "${MEMORY_UPDATES_COUNT} - 1")
            
            foreach(UPDATE_INDEX RANGE ${UPDATES_MAX})
                string(JSON MEMORY_UPDATE GET "${FEEDBACK_RESULT}" "memory_updates" ${UPDATE_INDEX})
                set(MEMORY_PATH ${state_dir}/memory.json)
                file(READ ${MEMORY_PATH} MEMORY_CONTENT)
                # Merge updates with current memory using CMake string manipulation
                file(WRITE ${MEMORY_PATH} "${MEMORY_CONTENT}")
            endforeach()
            
            # Check completion using CMake string manipulation
            string(JSON SHOULD_CONTINUE GET "${FEEDBACK_RESULT}" "continue_iteration")
            if(SHOULD_CONTINUE STREQUAL "false")
                set(SHOULD_CONTINUE false)
                message(STATUS "Task completed successfully.")
            endif()
            
            math(EXPR ITERATION_COUNT "${ITERATION_COUNT} + 1")
        endforeach()
        
        if(ITERATION_COUNT GREATER_EQUAL 10)
            message(WARNING "Warning: Maximum iterations reached")
        endif()
    endwhile()
endfunction()

# Start the feedback loop with work queue directory
run_feedback_loop("${TASK}" "${CMAKE_CURRENT_SOURCE_DIR}/work_queue")
