function(execute_llm PROMPT RESULT_VAR)
    # 8B09616B-1495-4070-AC50-F52D72E34238
    # Check for debug flags
    if(DEFINED DEBUG_SEND)
        message(STATUS "Debug mode enabled (SEND)")
        message(STATUS "Executing LLM call with prompt: ${PROMPT}")
        message(STATUS "Result will be stored in: ${RESULT_VAR}")
    endif

    file(READ "${CMAKE_BINARY_DIR}/llm_config.json" config_content)
    string(JSON config_without_brace GET "${config_content}" 1 -1)
    string(REPLACE "\"" "\\\"" ESCAPED_PROMPT "${PROMPT}")
    
    # Prepare request data
    set(request_data "{\"prompt\": \"${ESCAPED_PROMPT}\"}")
    
    # Debug send output
    if(DEFINED DEBUG_SEND)
        message(STATUS "Sending request to LLM API:")
        message(STATUS "Endpoint: ${LLM_API_ENDPOINT}")
        message(STATUS "Config: ${config_without_brace}")
        message(STATUS "Prompt: ${PROMPT}")
    endif
    
    set(script_content "#!/bin/bash\ncurl -S -X POST -H 'Content-Type: application/json' -d @${CMAKE_BINARY_DIR}/llm_config.json -d '${request_data}' ${LLM_API_ENDPOINT}")
    file(WRITE "${CMAKE_BINARY_DIR}/llm_api_call.sh" "${script_content}")
    
    execute_process(COMMAND bash "${CMAKE_BINARY_DIR}/llm_api_call.sh"
        OUTPUT_VARIABLE response
        RESULT_VARIABLE status
    )
    
    # Debug receive output
    if(DEFINED DEBUG_RECEIVE)
        message(STATUS "Received response from LLM API:")
        message(STATUS "${response}")
    endif
    
    file(REMOVE "${CMAKE_BINARY_DIR}/llm_api_call.sh")
    
    if(NOT status EQUAL 0)
        if(DEFINED DEBUG_SEND)
            message(STATUS "LLM API call failed with status: ${status}")
            message(STATUS "Response: ${response}")
        endif()
        message(FATAL_ERROR "LLM API call failed. Enable DEBUG_SEND for more details.")
    endif()
    
    set(${RESULT_VAR} "${response}" PARENT_SCOPE)
endfunction()

function(edit_file_by_coordinates FILE_PATH START_LINE END_LINE NEW_CONTENT)
    execute_process(COMMAND head -n $((START_LINE - 1)) "${FILE_PATH}" OUTPUT_VARIABLE head_output OUTPUT_STRIP_TRAILING_WHITESPACE)
    execute_process(COMMAND echo "${NEW_CONTENT}" OUTPUT_VARIABLE echo_output OUTPUT_STRIP_TRAILING_WHITESPACE)
    execute_process(COMMAND tail -n +$((END_LINE + 1)) "${FILE_PATH}" OUTPUT_VARIABLE tail_output OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(output "${head_output}\n${echo_output}\n${tail_output}")
    file(WRITE "${FILE_PATH}" "${output}")
endfunction()

function(llm_edit_code_by_coordinates FILE_PATH)
    set(PROMPT "Provide the start line, end line, and the new content to edit the file: ${FILE_PATH}")
    execute_llm("${PROMPT}" LLM_RESPONSE)

    string(STRIP "${LLM_RESPONSE}" LLM_RESPONSE_STRIPPED)
    message(STATUS "LLM Response: ${LLM_RESPONSE_STRIPPED}")

    if(LLM_RESPONSE MATCHES "START_LINE:([0-9]+)")
        string(REGEX MATCH "START_LINE:([0-9]+)" MATCH_START_LINE "${LLM_RESPONSE}")
        string(REGEX REPLACE "START_LINE:([0-9]+)" "\\1" START_LINE "${MATCH_START_LINE}")

        if(LLM_RESPONSE MATCHES "END_LINE:([0-9]+)")
            string(REGEX MATCH "END_LINE:([0-9]+)" MATCH_END_LINE "${LLM_RESPONSE}")
            string(REGEX REPLACE "END_LINE:([0-9]+)" "\\1" END_LINE "${MATCH_END_LINE}")

            if(LLM_RESPONSE MATCHES "NEW_CONTENT:(.*)")
                string(REGEX MATCH "NEW_CONTENT:(.*)" MATCH_NEW_CONTENT "${LLM_RESPONSE}")
                string(REGEX REPLACE "NEW_CONTENT:(.*)" "\\1" NEW_CONTENT "${MATCH_NEW_CONTENT}")

                edit_file_by_coordinates("${FILE_PATH}" "${START_LINE}" "${END_LINE}" "${NEW_CONTENT}")
            else()
                message(WARNING "LLM response does not contain NEW_CONTENT field")
            endif()
        else()
            message(WARNING "LLM response does not contain END_LINE field")
        endif()
    else()
        message(WARNING "LLM response does not contain START_LINE field")
    endif()
endfunction()
